import os
import smtplib
import schedule
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Load email credentials securely
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

# Ensure required variables are set
if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not TO_EMAIL:
    raise ValueError("❌ ERROR: Missing email credentials. Set EMAIL_ADDRESS, EMAIL_PASSWORD, and TO_EMAIL.")

# Load the text file dynamically
file_path = os.path.join(os.path.dirname(__file__), "bot_1_text.txt")
subject_file_path = os.path.join(os.path.dirname(__file__), "subject_lines.txt")

# Ensure text files exist
if not os.path.exists(file_path):
    raise FileNotFoundError("❌ ERROR: bot_1_text.txt file is missing!")

if not os.path.exists(subject_file_path):
    raise FileNotFoundError("❌ ERROR: subject_lines.txt file is missing!")

# Load bot_1_text.txt content into memory
with open(file_path, "r", encoding="utf-8") as f:
    text_lines = [line.strip() for line in f.readlines() if line.strip()]  # Remove empty lines

# Load subject_lines.txt content into memory
with open(subject_file_path, "r", encoding="utf-8") as f:
    subject_lines = [line.strip() for line in f.readlines() if line.strip()]  # Remove empty lines

# Track the current position in bot_1_text.txt
current_line = 0
lines_per_email = 5

def send_email():
    global current_line

    # Pick a random subject line
    subject = random.choice(subject_lines)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Ensure there is content to send
    if not text_lines:
        print(f"{timestamp} ❌ Error: The text file is empty or not loaded.")
        return

    # Get the next chunk of lines
    email_body = "\n".join(text_lines[current_line:current_line + lines_per_email])
    current_line += lines_per_email

    # Loop back to the beginning if we reach the end
    if current_line >= len(text_lines):
        current_line = 0

    print(f"{timestamp} Preparing email...\nSubject: {subject}\nBody:\n{email_body}\n")

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(email_body, "plain"))

    try:
        print(f"{timestamp} Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        print(f"{timestamp} Sending email...")
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

print("Email bot is running... Press CTRL + C to stop.")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
