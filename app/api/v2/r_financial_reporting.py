from fastapi import APIRouter

router = APIRouter()

@router.get("/trial-balance")
def get_trial_balance():
    return {"message": "Trial Balance"}

@router.get("/general-ledger")
def get_general_ledger():
    return {"message": "General Ledger"}

@router.get("/final-reports")
def get_final_reports():
    return {"message": "Final Reports"}
