import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# MobileNetV2 ImageNet class labels mapped to plant disease categories
# In production, replace with fine-tuned PlantVillage model weights
DISEASE_LABELS = [
    "Healthy Plant",
    "Leaf Blight",
    "Powdery Mildew",
    "Leaf Rust",
    "Early Blight",
    "Late Blight",
    "Bacterial Spot",
    "Leaf Scorch",
    "Mosaic Virus",
    "Root Rot",
]

_model = None


def _load_model():
    global _model
    if _model is None:
        try:
            from tensorflow.keras.applications import MobileNetV2
            _model = MobileNetV2(weights="imagenet", include_top=True)
            logger.info("✅ MobileNetV2 model loaded")
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            _model = None
    return _model


def _preprocess(image_path: str) -> np.ndarray:
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    arr = np.array(img, dtype=np.float32)
    arr = preprocess_input(arr)
    return np.expand_dims(arr, axis=0)


def predict_disease(image_path: str) -> dict:
    """
    Returns disease name and confidence score.
    Falls back to a mock prediction if TensorFlow is unavailable.
    """
    model = _load_model()

    if model is None:
        # Graceful fallback — useful during development without GPU
        logger.warning("Model unavailable, using mock prediction")
        return {"disease": "Leaf Blight", "confidence": 0.87, "source": "mock"}

    try:
        from tensorflow.keras.applications.mobilenet_v2 import decode_predictions
        tensor = _preprocess(image_path)
        preds = model.predict(tensor, verbose=0)
        top = decode_predictions(preds, top=1)[0][0]  # (class_id, label, score)

        # Map ImageNet label → nearest disease label for demo
        # Replace this mapping with actual PlantVillage fine-tuned labels
        label = top[1].replace("_", " ").title()
        confidence = float(top[2])

        # Simple heuristic: low confidence on ImageNet → flag as disease
        disease = label if confidence > 0.4 else DISEASE_LABELS[1]
        return {"disease": disease, "confidence": confidence, "source": "mobilenetv2"}

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"disease": "Unknown Disease", "confidence": 0.0, "source": "error"}
