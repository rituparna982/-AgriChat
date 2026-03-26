import logging
import datetime
from fastapi import APIRouter, Request, HTTPException

from database.mongo import farmers_col, queries_col
from services.ai_service import get_disease_advice, get_text_advice
from services.cv_model import predict_disease
from utils.telegram_helpers import send_message, download_file, transcribe_voice

logger = logging.getLogger(__name__)
router = APIRouter()

WELCOME_MSG = (
    "👋 *Welcome to Smart Agriculture Assistant!*\n\n"
    "I can help you with:\n"
    "🌿 Crop disease diagnosis\n"
    "📸 Send a crop photo for instant analysis\n"
    "🎤 Send a voice message with your question\n"
    "💬 Type any farming question\n\n"
    "Use /help for more info."
)

HELP_MSG = (
    "📖 *How to use this bot:*\n\n"
    "1️⃣ *Text* — Type your crop problem\n"
    "2️⃣ *Photo* — Send a crop image for disease detection\n"
    "3️⃣ *Voice* — Record your question in any language\n\n"
    "Example: _'My tomato leaves are turning yellow'_\n"
    "Then send a photo for AI-powered diagnosis."
)


async def _upsert_farmer(telegram_id: int, name: str) -> None:
    await farmers_col().update_one(
        {"telegram_id": telegram_id},
        {"$setOnInsert": {"telegram_id": telegram_id, "name": name, "location": None, "crop_type": None}},
        upsert=True,
    )


async def _save_query(farmer_id: int, **kwargs) -> None:
    record = {
        "farmer_id": farmer_id,
        "timestamp": datetime.datetime.utcnow(),
        **kwargs,
    }
    await queries_col().insert_one(record)


@router.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    message = body.get("message") or body.get("edited_message")
    if not message:
        return {"ok": True}

    chat_id: int = message["chat"]["id"]
    user = message.get("from", {})
    name = user.get("first_name", "Farmer")

    await _upsert_farmer(chat_id, name)

    # ── Commands ──────────────────────────────────────────────
    if "text" in message:
        text: str = message["text"].strip()

        if text == "/start":
            await send_message(chat_id, WELCOME_MSG)
            return {"ok": True}

        if text == "/help":
            await send_message(chat_id, HELP_MSG)
            return {"ok": True}

        # General text query
        await send_message(chat_id, "🔍 Analyzing your question...")
        ai_reply = await get_text_advice(text)
        await send_message(chat_id, ai_reply)
        await _save_query(chat_id, message_text=text, ai_response=ai_reply)
        return {"ok": True}

    # ── Voice ─────────────────────────────────────────────────
    if "voice" in message:
        file_id = message["voice"]["file_id"]
        await send_message(chat_id, "🎤 Processing your voice message...")
        transcribed = await transcribe_voice(file_id)
        await send_message(chat_id, f"📝 I heard: _{transcribed}_")

        ai_reply = await get_text_advice(transcribed)
        await send_message(chat_id, ai_reply)
        await _save_query(chat_id, message_text=transcribed, ai_response=ai_reply)
        return {"ok": True}

    # ── Image ─────────────────────────────────────────────────
    if "photo" in message:
        await send_message(chat_id, "📸 Analyzing your crop image...")

        # Telegram sends multiple sizes; pick the largest
        photo = message["photo"][-1]
        image_path = await download_file(photo["file_id"], "jpg")

        result = predict_disease(image_path)
        disease = result["disease"]
        confidence = result["confidence"]

        ai_reply = await get_disease_advice(disease, confidence)

        response_text = (
            f"🔬 *Detected:* {disease} ({confidence:.0%} confidence)\n\n"
            f"{ai_reply}"
        )
        await send_message(chat_id, response_text)
        await _save_query(
            chat_id,
            image_path=image_path,
            disease_prediction=f"{disease} ({confidence:.0%})",
            ai_response=ai_reply,
        )
        return {"ok": True}

    # Unsupported message type
    await send_message(chat_id, "Please send text, a voice message, or a crop photo. 🌱")
    return {"ok": True}
