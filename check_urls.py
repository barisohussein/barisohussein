import requests
import smtplib
from email.mime.text import MIMEText
import os

# --- STEP 1: Define URLs to check ---
urls_to_check = [
    "https://www.brooksrunning.com/en_us/featured/unisex-running-shoes/hyperion-elite-5/100049.html",
    "https://www.amazon.com/404",
    # Add more URLs here
]

# --- STEP 2: Check status of URLs ---
def get_broken_urls(urls):
    broken = []
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                broken.append((url, response.status_code))
        except Exception as e:
            broken.append((url, str(e)))
    return broken

# --- STEP 3: Send Email Alert ---
def send_email(broken_urls):
    sender = os.environ['EMAIL_USERNAME']
    password = os.environ['EMAIL_PASSWORD']
    recipient = os.environ['EMAIL_RECIPIENT']

    subject = "[Alert] Broken URLs Detected"
    body = "The following URLs returned an error:\n\n"
    for url, status in broken_urls:
        body += f"{url} - {status}\n"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

# --- STEP 4: Run the check ---
if __name__ == "__main__":
    broken = get_broken_urls(urls_to_check)
    if broken:
        send_email(broken)
    else:
        print("✅ All URLs are live.")
