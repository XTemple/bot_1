import os
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Load email credentials securely from environment variables
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

if not TO_EMAIL:
    raise ValueError("❌ ERROR: Missing recipient email. Set the TO_EMAIL environment variable.")

# Load the text file into memory
file_path = os.path.join(os.path.dirname(__file__), "bot_1_text.txt")

if not file_path:
    raise ValueError("❌ ERROR: Missing file path. Set the BOT_FILE_PATH environment variable.")

with open(file_path, "r", encoding="utf-8") as f:
    text_lines = [line.strip() for line in f.readlines() if line.strip()]  # Remove empty lines

# Track the current position in the file
current_line = 0
lines_per_email = 5

import datetime

def send_email():
    global current_line

    subject = "My Working Duties"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Ensure there is content to send
    if not text_lines:
        print(f"{timestamp} ❌ Error: The text file is empty or not loaded.")
        return

    email_body = "\n".join(text_lines[current_line:current_line + lines_per_email])
    current_line += lines_per_email

    # Loop back to the beginning if we reach the end
    if current_line >= len(text_lines):
        current_line = 0

    print(f"{timestamp} 📨 Preparing email...\nSubject: {subject}\nBody:\n{email_body}\n")

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(email_body, "plain"))

    try:
        print(f"{timestamp} 🔄 Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        print(f"{timestamp} 📨 Sending email...")
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())
        server.quit()
        print(f"{timestamp} ✅ Email sent successfully! Sent lines {current_line - lines_per_email} to {current_line - 1}")

    except smtplib.SMTPRecipientsRefused:
        print(f"{timestamp} ❌ Email blocked: The recipient refused the email.")
    except smtplib.SMTPServerDisconnected:
        print(f"{timestamp} ❌ Connection lost: Server disconnected before sending.")
    except smtplib.SMTPResponseException as e:
        error_code = e.smtp_code
        error_message = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
        print(f"{timestamp} ❌ SMTP Error {error_code}: {error_message}")
    except Exception as e:
        print(f"{timestamp} ❌ Unknown error: {e}")

# Schedule the function to send an email every 3 minutes
schedule.every(3).minutes.do(send_email)

print("📨 Email bot is running... Press CTRL + C to stop.")

# To send a test email
# send_email()

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
