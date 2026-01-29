from fastapi import APIRouter

router = APIRouter()

@router.get("/bank-invoices")
def reconcile_bank_invoices():
    return {"message": "Reconcile Bank and Invoices"}

@router.get("/bank-receipts-bills")
def reconcile_bank_receipts_bills():
    return {"message": "Reconcile Bank, Receipts, and Bills"}

@router.get("/bills-receipts")
def reconcile_bills_receipts():
    return {"message": "Reconcile Bills and Receipts"}
