from pydantic import BaseModel

class EmailReminderRequest(BaseModel):
    vendor:str
    invoice_number: str
    due_date: str
    balance_due: float
