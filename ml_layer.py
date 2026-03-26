import os
import random
try:
    import tensorflow as tf
    from tensorflow.keras.preprocessing import image
    from tensorflow.keras.models import load_model
    from PIL import Image
    import numpy as np
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

# DAY 3: CNN Inference Layer

MODEL_PATH = "crop_disease_model.h5"

# Load the model if it exists
model = None
try:
    if TF_AVAILABLE and os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
except:
    pass

# Generic crop diseases for fallback mockup if model is not yet trained
MOCK_DISEASES = ["Tomato Early Blight", "Potato Late Blight", "Healthy Crop", "Corn Leaf Rust", "Apple Scab"]

def predict_crop_disease(image_path: str) -> str:
    """
    Takes an image file path and uses the CNN to predict the disease.
    If the CNN .h5 file doesn't exist yet, it returns a simulated fallback prediction
    with a mock confidence score.
    """
    if model is None or not TF_AVAILABLE:
        # Fallback simulation
        disease = random.choice(MOCK_DISEASES)
        confidence = round(random.uniform(0.75, 0.99), 2)
        return f"{disease} (Confidence: {confidence * 100}%)"
    
    try:
        # Load and preprocess image
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Normalize
        
        # Predict
        predictions = model.predict(img_array)
        class_idx = np.argmax(predictions[0])
        confidence = predictions[0][class_idx]
        
        # Load classes mapping (mocked for simplicity here)
        # Ideally you load class_indices.json created during training
        predicted_disease = f"Class Index {class_idx}" 
        
        return f"{predicted_disease} (Confidence: {confidence * 100:.2f}%)"
    except Exception as e:
        return f"Error analyzing image: {str(e)}"
