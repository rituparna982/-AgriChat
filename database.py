import motor.motor_asyncio
import os

# Connect to MongoDB (Default is localhost)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Create a MongoDB client using Motor (Async driver for FastAPI)
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

# Connect to our 'agri_chatbot' database
db = client.agri_chatbot

# Collections
farmers_collection = db.get_collection("farmers")
queries_collection = db.get_collection("queries")
