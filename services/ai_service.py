import os
import logging
from google import genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.0-flash"


async def get_disease_advice(disease: str, confidence: float) -> str:
    prompt = (
        f"You are an agriculture expert. A farmer's crop has been diagnosed with: {disease} "
        f"(confidence: {confidence:.0%}). "
        "Explain the disease in simple language (2-3 sentences) and provide 3 practical treatment steps. "
        "Keep the response concise and farmer-friendly."
    )
    try:
        response = _client.models.generate_content(model=MODEL, contents=prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"Disease detected: {disease}. Please consult your local agricultural extension officer for treatment advice."


async def get_text_advice(user_message: str) -> str:
    prompt = (
        "You are a helpful agriculture assistant for farmers. "
        f"Farmer's question: {user_message}\n"
        "Give a concise, practical answer in simple language. If it's about crop disease, "
        "ask them to send a photo for better diagnosis."
    )
    try:
        response = _client.models.generate_content(model=MODEL, contents=prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "I'm having trouble processing your request. Please try again shortly."
