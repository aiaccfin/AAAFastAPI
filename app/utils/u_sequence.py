# app/db/sequence.py

from app.db.x_mg_conn import db  # assuming you have this
from pymongo import ReturnDocument

async def get_next_sequence(name: str) -> int:
    result = await db.counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return result["seq"]
