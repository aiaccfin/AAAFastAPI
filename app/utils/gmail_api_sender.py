# app/utils/gmail_api_sender.py

import os
import base64
import random
import secrets
import string
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.db.x_mg_conn import verification_collection

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = "./credentials.json"
TOKEN_FILE = "./token.json"

def generate_ascii_verification_code(length=6):
    chars =  string.digits 
    return ''.join(secrets.choice(chars) for _ in range(length))



# def get_gmail_service():
#     creds = None
#     if os.path.exists(TOKEN_FILE):
#         creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
#             creds = flow.run_local_server(port=0, open_browser=False)
#         with open(TOKEN_FILE, "w") as token:
#             token.write(creds.to_json())

#     return build("gmail", "v1", credentials=creds)


def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # 🔁 Check and refresh token explicitly if expired
    if creds:
        if creds.expired and creds.refresh_token:
            print("[INFO] Access token expired. Refreshing...")
            try:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"[ERROR] Token refresh failed: {e}")
                raise
    else:
        print("[INFO] No valid credentials found. Starting OAuth flow.")
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0, open_browser=False)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)



async def generate_and_send_verification_code(email: str):
    code = generate_ascii_verification_code()

    await verification_collection.delete_many({"email": email})
    await verification_collection.insert_one({"email": email, "code": code})

    subject = "Verification Code from xAIBooks"
    body = f"Your verification code is: {code}. Please check Spam folder if you don't see it in your inbox."

    message = MIMEText(body)
    message["to"] = email
    message["from"] = "me"
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service = get_gmail_service()
        send_message = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        print(f"Email sent to {email}, ID: {send_message['id']}")
    except Exception as e:
        print(f"Failed to send email: {e}")
