import os

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_AIACCFIN")
DB_NAME = "db_fastapi"

client = AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]
users_collection = database["col_user"]
