import logging
import os
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from database.mongo import connect_db, close_db
from routes.telegram_webhook import router as telegram_router
from services.ai_service import get_text_advice, get_disease_advice
from services.cv_model import predict_disease

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await connect_db()
    except Exception as e:
        logger.warning(f"MongoDB not available: {e}. Running without database.")
    yield
    try:
        await close_db()
    except Exception:
        pass


app = FastAPI(
    title="Smart Agriculture Assistant",
    description="AI-powered crop disease detection via Telegram Bot",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telegram_router, prefix="/telegram", tags=["Telegram"])


# ── Direct Chat API for Frontend ─────────────────────────────────


class ChatRequest(BaseModel):
    message: str


@app.post("/chat", tags=["Chat"])
async def direct_chat(req: ChatRequest):
    """Direct chat endpoint for the React frontend."""
    try:
        ai_reply = await get_text_advice(req.message)
        return {"response": ai_reply}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"response": "I'm having trouble processing your request. Please try again."}


@app.post("/chat/image", tags=["Chat"])
async def chat_image(image: UploadFile = File(...), message: str = Form("")):
    """Image analysis endpoint for the React frontend."""
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(image.filename or "upload.jpg")[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await image.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = predict_disease(tmp_path)
        disease = result["disease"]
        confidence = result["confidence"]
        ai_reply = await get_disease_advice(disease, confidence)

        # Clean up temp file
        os.unlink(tmp_path)

        return {
            "response": f"🔬 **Detected:** {disease} ({confidence:.0%} confidence)\n\n{ai_reply}",
            "disease": disease,
            "confidence": confidence,
        }
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return {"response": "Failed to analyze the image. Please try again."}


# ── Health & Dashboard ────────────────────────────────────────────


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "running", "service": "Smart Agriculture Assistant"}


@app.get("/farmers", tags=["Dashboard"])
async def list_farmers():
    try:
        from database.mongo import farmers_col
        docs = await farmers_col().find({}, {"_id": 0}).to_list(100)
        return docs
    except Exception:
        return []


@app.get("/queries", tags=["Dashboard"])
async def list_queries():
    try:
        from database.mongo import queries_col
        docs = await queries_col().find({}, {"_id": 0}).to_list(100)
        return docs
    except Exception:
        return []
