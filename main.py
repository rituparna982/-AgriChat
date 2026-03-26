import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database.mongo import connect_db, close_db
from routes.telegram_webhook import router as telegram_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


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


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "running", "service": "Smart Agriculture Assistant"}


@app.get("/farmers", tags=["Dashboard"])
async def list_farmers():
    from database.mongo import farmers_col
    docs = await farmers_col().find({}, {"_id": 0}).to_list(100)
    return docs


@app.get("/queries", tags=["Dashboard"])
async def list_queries():
    from database.mongo import queries_col
    docs = await queries_col().find({}, {"_id": 0}).to_list(100)
    return docs
