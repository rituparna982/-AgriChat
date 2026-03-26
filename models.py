from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Schema for storing user/farmer data in MongoDB
class FarmerSchema(BaseModel):
    phone_number: str = Field(...)
    language: str = Field(default="english")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
# Schema for logging chat queries
class QuerySchema(BaseModel):
    phone_number: str
    query_text: str = Field(default="")
    query_type: str # 'text', 'image', 'voice'
    bot_response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
