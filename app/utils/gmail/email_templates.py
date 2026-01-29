from datetime import datetime, date

def verification_template(code: str) -> tuple[str, str]:
    subject = "Verification Code from xAIBooks"
    body = f"Your verification code is: {code}. Please check Spam folder if you don't see it in your inbox."
    return subject, body

def invoice_reminder_template(vendor: str, invoice_number: str, due_date: str, balance_due: float) -> tuple[str, str]:
    # subject = f"Reminder: Invoice #{invoice_number} is Due TODAY!"
    # Convert due_date string to date object
    try:        
        due_date_obj = datetime.strptime(due_date.replace('.', ''), "%b%d, %Y").date()
    except ValueError:
        # Fallback if due_date is not in the expected format
        subject = f"Reminder: Invoice #{invoice_number}"
    else:
        today = date.today()
        if due_date_obj == today:
            subject = f"Reminder: Invoice #{invoice_number} is Due TODAY!"
        elif due_date_obj < today:
            days_late = (today - due_date_obj).days
            subject = f"Reminder: Invoice #{invoice_number} is past due for {days_late} day{'s' if days_late > 1 else ''}!"
        else:
            subject = f"Reminder: Invoice #{invoice_number} is due on {due_date}"
    
    body = f"""
      <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Dear Valued Customer,</p>

        <p>This is a friendly reminder from <strong>xAIBooks Automatical Accounting</strong>.</p>

        <table style="border-collapse: collapse; margin: 15px 0;">
          <tr>
            <td style="padding: 8px; font-weight: bold;">Vendor:</td>
            <td style="padding: 8px;">{vendor}</td>
          </tr>
          <tr>
            <td style="padding: 8px; font-weight: bold;">Invoice Number:</td>
            <td style="padding: 8px;">#{invoice_number}</td>
          </tr>
          <tr>
            <td style="padding: 8px; font-weight: bold;">Due Date:</td>
            <td style="padding: 8px;">{due_date}</td>
          </tr>
          <tr>
            <td style="padding: 8px; font-weight: bold;">Balance Due:</td>
            <td style="padding: 8px;">${balance_due:.2f}</td>
          </tr>
        </table>

        <p>Please ensure timely payment to avoid any penalties.</p>
        <p>Thank you!</p>
        
        <p style="margin-top: 30px;">Sincerely,<br>xAIBooks Team</p>
      </body>
    """
    return subject, body
