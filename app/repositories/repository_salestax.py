# app/repositories/gst26_repository.py
from motor.motor_asyncio import AsyncIOMotorCollection
from app.schemas.schema_salestax import GST26Create
import uuid
from datetime import datetime

class GST26Repository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_entry(self, entry: GST26Create) -> dict:
        entry_dict = entry.dict()

        # Internal only: generate MongoDB _id
        entry_dict["_id"] = str(uuid.uuid4())

        await self.collection.insert_one(entry_dict)
        return entry_dict


    async def fetch_all(self) -> list[dict]:
        cursor = self.collection.find()
        entries = [entry async for entry in cursor]
        return entries
    
    
    
    async def update_entry(self, entry_id: str, update_data: dict) -> dict:
        # Remove _id from update to prevent overwriting
        update_data.pop("_id", None)

        updated_doc = await self.collection.find_one_and_update(
            {"_id": entry_id},
            {"$set": update_data},
            return_document=True  # returns the updated document
        )

        if not updated_doc:
            raise ValueError(f"GST26 entry {entry_id} not found")

        return updated_doc