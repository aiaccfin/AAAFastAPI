from typing import List
from bson import ObjectId
from fastapi import APIRouter
from app.db.x_mg_conn import db
from app.schemas.s_dblog import DBLogModel

router = APIRouter()

@router.get("/")
def get_dashboard():
    return {
        "message": "Welcome to the Dashboard",
        "notifications": {
            "bank_statement": "No new messages",
            "receipt_bill_logs": "No new messages",
            "invoice_summary": "No new messages"
        }
    }


@router.get("/logs")
async def get_all_logs():
    logs = await db.crud_logs.find().sort("timestamp", -1).to_list(100)

    for log in logs:
        # convert top-level _id
        if "_id" in log and isinstance(log["_id"], ObjectId):
            log["_id"] = str(log["_id"])

        # convert nested _id in data (if present)
        if "data" in log and isinstance(log["data"], dict):
            if "_id" in log["data"] and isinstance(log["data"]["_id"], ObjectId):
                log["data"]["_id"] = str(log["data"]["_id"])

        # also make sure document_id is string
        if "document_id" in log and isinstance(log["document_id"], ObjectId):
            log["document_id"] = str(log["document_id"])

    return logs

