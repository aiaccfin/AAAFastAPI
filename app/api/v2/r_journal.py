from fastapi import APIRouter

router = APIRouter()

@router.get("/bank")
def get_bank_journal():
    return {"message": "Bank Journal"}

@router.get("/bill")
def get_bill_journal():
    return {"message": "Bill Journal"}

@router.get("/invoice")
def get_invoice_journal():
    return {"message": "Invoice Journal"}

@router.get("/receipt")
def get_receipt_journal():
    return {"message": "Receipt Journal"}

@router.get("/")
def get_bank_journal():
    return {"message": "Journals"}
