import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # Replace with your actual URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["db_xai"]  # Adjust based on your DB name

async def get_mongo_client():
    return client
