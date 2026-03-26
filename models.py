from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FarmerSchema(BaseModel):
    telegram_id: int
    name: str
    location: Optional[str] = None
    crop_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QuerySchema(BaseModel):
    farmer_id: int
    message_text: Optional[str] = None
    image_path: Optional[str] = None
    disease_prediction: Optional[str] = None
    ai_response: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
