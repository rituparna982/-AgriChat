from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import farmers_collection
from models import FarmerSchema
import requests
import os
import datetime

from ml_layer import predict_crop_disease
from gemini_service import analyze_farmer_query
from database import queries_collection

# Initialize FastAPI app
app = FastAPI(
    title="AgriChatbot API",
    description="Backend for AI-Powered Agricultural Advisory Chatbot using WhatsApp"
)

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the AgriChatbot API! Server is running."}

@app.post("/register_farmer/", tags=["Farmers"])
async def register_farmer(farmer: FarmerSchema):
    farmer_dict = farmer.dict()
    
    # Check if farmer is already saved in DB
    existing = await farmers_collection.find_one({"phone_number": farmer.phone_number})
    if existing:
        return {"status": "Farmer already registered"}
    
    # Insert new farmer into MongoDB
    new_farmer = await farmers_collection.insert_one(farmer_dict)
    return {"status": "Farmer registered successfully", "id": str(new_farmer.inserted_id)}

@app.post("/webhook/", tags=["WhatsApp"])
async def whatsapp_webhook(request: Request):
    # Twilio sends data as form-urlencoded
    form_data = await request.form()
    
    sender = form_data.get("From", "")
    message_body = form_data.get("Body", "").strip()
    num_media = int(form_data.get("NumMedia", 0))
    media_content_type = form_data.get("MediaContentType0", "")
    media_url = form_data.get("MediaUrl0", "")

    # 1. Identify Input Type
    query_type = "text"
    if num_media > 0:
        if "image" in media_content_type:
            query_type = "image"
        elif "audio" in media_content_type or "voice" in media_content_type or "video" in media_content_type:
            query_type = "voice"
            
    # 2. Download Media if present
    media_path = None
    if query_type in ["image", "voice"] and media_url:
        media_path = download_twilio_media(media_url, query_type)

    # 3. AI Processing
    cnn_diagnosis = None
    if query_type == "image" and media_path:
        cnn_diagnosis = predict_crop_disease(media_path)
        
    ai_response = analyze_farmer_query(
        query_type=query_type,
        text_input=message_body,
        media_path=media_path,
        cnn_diagnosis=cnn_diagnosis
    )
    
    print(f"Received [{query_type}] from {sender}")
    print(f"Media Path: {media_path}")
    print(f"AI Response Pattern Generated")

    # 4. Save to Database
    query_record = {
        "phone_number": sender,
        "query_text": message_body,
        "query_type": query_type,
        "bot_response": ai_response,
        "timestamp": datetime.datetime.utcnow()
    }
    await queries_collection.insert_one(query_record)

    # In a fully integrated flow, you would call the Twilio API here to reply to WhatsApp
    # e.g., client.messages.create(body=ai_response, from_='whatsapp:+...yours', to=sender)

    return {"status": "success", "message_type": query_type, "response": ai_response}

@app.get("/farmers/", tags=["Dashboard"])
async def get_farmers():
    farmers_cursor = farmers_collection.find({})
    farmers = await farmers_cursor.to_list(length=100)
    for f in farmers:
        f["_id"] = str(f["_id"])
    return farmers

@app.get("/queries/", tags=["Dashboard"])
async def get_queries():
    queries_cursor = queries_collection.find({})
    queries = await queries_cursor.to_list(length=100)
    for q in queries:
        q["_id"] = str(q["_id"])
    return queries

def download_twilio_media(media_url: str, media_type: str) -> str:
    """Download media from Twilio to local disk"""
    os.makedirs("downloads", exist_ok=True)
    
    response = requests.get(media_url)
    ext = ".jpg" if media_type == "image" else ".ogg"
    filepath = f"downloads/temp_{media_type}{ext}"
    
    with open(filepath, "wb") as f:
        f.write(response.content)
        
    return filepath

def convert_audio_to_text(audio_path: str) -> str:
    """
    Placeholder for Voice->Text. 
    Since Gemini 1.5 Flash supports direct audio inputs natively, 
    we will pass the audio file directly to Gemini in Day 4! 
    This saves us from needing a separate external speech-to-text API.
    """
    return "[Transcription pending - Will use Gemini Audio Input in Day 4]"

# How to run locally:
# uvicorn main:app --reload
