import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "smart_agri"

client: AsyncIOMotorClient = None


async def connect_db():
    global client
    client = AsyncIOMotorClient(MONGODB_URI)
    await client.admin.command("ping")
    logger.info("✅ MongoDB connected successfully")


async def close_db():
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_db():
    return client[DB_NAME]


def farmers_col():
    return get_db()["farmers"]


def queries_col():
    return get_db()["queries"]
