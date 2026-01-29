from app.utils.gmail.gmail_service import send_email
from app.utils.gmail.email_templates import invoice_reminder_template

def send_invoice_reminder(vendor: str, invoice_number: str, due_date: str, balance_due: float):
    subject, body = invoice_reminder_template(vendor, invoice_number, due_date, balance_due)
    send_email(to="kevin@receiptcanada.com", subject=subject, body=body)
    # send_email(to="leoreny8@gmail.com", subject=subject, body=body)
