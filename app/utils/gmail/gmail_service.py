import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = "./credentials.json"
TOKEN_FILE = "./token.json"

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def send_email(to: str, subject: str, body: str, from_email: str = "receiptcanada01@gmail.com"):
    message = MIMEText(body, "html")
    message["to"] = to
    message["from"] = from_email
    message["subject"] = subject
    message["bcc"] = "aiaccfin@gmail.com"

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service = get_gmail_service()
    send_message = service.users().messages().send(
        userId="me", body={"raw": raw_message}
    ).execute()
    print(f"Email sent from{from_email} to {to}, ID: {send_message['id']}")
