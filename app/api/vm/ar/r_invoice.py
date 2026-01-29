from typing import Any, Dict
from fastapi import APIRouter,HTTPException
from datetime import datetime
import uuid

from app.models.m_user import Role
from app.schemas.s_invoice import InvoiceModel
from app.schemas.s_email_reminder import EmailReminderRequest
from app.db.x_mg_conn import invoice_collection
from app.utils.u_load_invoice import load_invoice_from_file
from app.utils.gmail.senders.invoice_sender import send_invoice_reminder

router = APIRouter()

@router.post("/new", response_model=InvoiceModel)
async def create_invoice(invoice: InvoiceModel):
    """
    Create a new invoice in MongoDB with server-side timestamps.
    """
    try:
        invoice_dict = invoice.dict()
        invoice_dict["_id"] = str(uuid.uuid4())

        result = await invoice_collection.insert_one(invoice_dict)

        return invoice_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.patch("/modify/{inv_number}", response_model=InvoiceModel)
async def modify_invoice(inv_number: str, update_data: Dict[str, Any]):
    """
    Modify an existing invoice identified by inv_number.
    Only the fields provided in update_data will be updated.
    """
    try:
        # Prevent accidental overwrites of immutable or system fields
        update_data.pop("_id", None)
        update_data.pop("inv_number", None)

        # Perform the update and return the new document
        updated_invoice = await invoice_collection.find_one_and_update(
            {"inv_number": inv_number},
            {"$set": update_data},
            return_document=True  # Return the updated document (requires motor 3.0+)
        )

        if not updated_invoice:
            raise HTTPException(status_code=404, detail=f"Invoice {inv_number} not found")

        # If you use UUID for _id, it's already JSON-safe — no conversion needed
        return updated_invoice

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load", response_model=Dict[str, Any])
async def import_invoice():
    """
    Load an invoice from file and insert it into MongoDB.
    Generates a UUID _id for the document.
    """
    try:
        # Load invoice data from file and validate
        raw_invoice_data = load_invoice_from_file()
        invoice = InvoiceModel(**raw_invoice_data)

        # Convert to dict and assign UUID _id
        invoice_dict = invoice.dict()
        invoice_dict["_id"] = str(uuid.uuid4())  # or uuid.uuid4() if no uuid6 lib

        # Insert into Mongo
        result = await invoice_collection.insert_one(invoice_dict)

        return {
            "status": "success",
            "inserted_id": invoice_dict["_id"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load invoice: {e}")
    
    
    
    
@router.get("/list")
async def get_invoices():
    """
    Retrieve all invoices from MongoDB (UUID-based _id).
    """
    try:
        invoices = [invoice async for invoice in invoice_collection.find()]
        return {
            "count": len(invoices),
            "invoices": invoices
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {e}")
    



@router.post("/email-reminder")
def send_invoice_email(data: EmailReminderRequest):
    try:
        send_invoice_reminder(
            vendor=data.vendor,
            invoice_number=data.invoice_number,
            due_date=data.due_date,
            balance_due=data.balance_due,
        )
        return {"message": "Reminder email sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

@router.post("/email-received")
def send_email_received(data: EmailReminderRequest):
    try:
        send_invoice_reminder(
            vendor=data.vendor,
            invoice_number=data.invoice_number,
            due_date=data.due_date,
            balance_due=data.balance_due,
        )
        return {"message": "Thank you email sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.delete("/delete/{inv_number}")
async def delete_invoice(inv_number: str):
    """
    Hard-delete an invoice by inv_number.
    """
    try:
        result = await invoice_collection.delete_one({"inv_number": inv_number})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Invoice {inv_number} not found")

        return {"message": f"Invoice {inv_number} has been permanently deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
