import secrets
import string
from app.db.x_mg_conn import verification_collection
from app.utils.gmail.gmail_service import send_email
from app.utils.gmail.email_templates import verification_template

def generate_code(length=44):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

async def send_verification_code(email: str):
    code = generate_code()
    await verification_collection.delete_many({"email": email})
    await verification_collection.insert_one({"email": email, "code": code})

    subject, body = verification_template(code)
    send_email(to=email, subject=subject, body=body)
