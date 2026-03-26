import os
import logging
import httpx
import speech_recognition as sr
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def send_message(chat_id: int, text: str) -> None:
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        )


async def get_file_url(file_id: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{TELEGRAM_API}/getFile", params={"file_id": file_id})
        data = resp.json()
        file_path = data["result"]["file_path"]
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"


async def download_file(file_id: str, extension: str) -> str:
    url = await get_file_url(file_id)
    dest = os.path.join(DOWNLOAD_DIR, f"{file_id}.{extension}")
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        with open(dest, "wb") as f:
            f.write(resp.content)
    logger.info(f"Downloaded file → {dest}")
    return dest


async def transcribe_voice(file_id: str) -> str:
    """Download OGG voice note, convert to WAV, transcribe with SpeechRecognition."""
    ogg_path = await download_file(file_id, "ogg")
    wav_path = ogg_path.replace(".ogg", ".wav")

    try:
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        logger.info(f"Transcribed: {text}")
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio. Please try again or type your question."
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return "Voice transcription failed. Please type your question instead."
    finally:
        for path in [ogg_path, wav_path]:
            if os.path.exists(path):
                os.remove(path)
