import google.generativeai as genai
import os
import pathlib

# DAY 4: AI Intelligence Layer
# Load your Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here") # Set this in your local .env file
genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 1.5 Flash (Supports Text + Audio + Images directly!)
model = genai.GenerativeModel("gemini-1.5-flash")

def analyze_farmer_query(query_type: str, text_input: str = "", media_path: str = None, cnn_diagnosis: str = None) -> str:
    """
    Constructs the prompt and calls Gemini API specifically tailored for farming advice.
    Ensures no hallucination by strictly constraining the prompt.
    """
    system_instruction = (
        "You are an expert agricultural AI assistant. Your goal is to help a farmer. "
        "Provide a simple, easy-to-understand explanation and practical treatment steps. "
        "If you do not know the answer or the query is not related to farming/agriculture, politely decline. "
        "Always respond in the language the user speaks in. Keep it concise, around 2-3 short paragraphs max."
    )
    
    prompt = f"{system_instruction}\n\n"
    content_list = [prompt]

    if query_type == "text":
        content_list.append(f"Farmer Query: {text_input}")
        
    elif query_type == "image":
        prompt += f"Our CNN image model detected: {cnn_diagnosis}. Explain this disease and give treatment advice. Farmer also said: {text_input}"
        content_list = [prompt] # Don't need to pass image again since CNN detected it, but we could!
        
        # We can also directly pass the image to Gemini as fallback/verification!
        if media_path and os.path.exists(media_path):
            img_file = genai.upload_file(media_path)
            content_list.append(img_file)

    elif query_type == "voice":
        prompt += f"The farmer sent a voice note. Please transcribe it, analyze their agricultural problem, and provide a solution."
        content_list = [prompt]
        if media_path and os.path.exists(media_path):
            audio_file = genai.upload_file(media_path)
            content_list.append(audio_file)

    try:
        response = model.generate_content(content_list)
        return response.text
    except Exception as e:
        return f"⚠️ AI Generation Error: {str(e)}\n\n(Ensure your Gemini API Key is valid!)"
