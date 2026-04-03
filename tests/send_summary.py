
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


EMAIL_USER = "barisobrooks@gmail.com"
EMAIL_APP_PASSWORD = "wtmc fofd lptd hepp"
# Recipient
TO_EMAIL = "barisohussein3@gmail.com"

# Example shift summary
shift_summary = """
Wells Fargo - Aurora Avenue: 09:00 AM - 12:00 PM | Saturday 04/04/26
Bank of America - Main Street: 01:00 PM - 04:00 PM | Sunday 04/05/26
"""

try:
    # Create message
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL
    msg["Subject"] = "Test: LISA Shift Summary"
    msg.attach(MIMEText(shift_summary, "plain"))

    # Connect to Gmail SMTP server
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_USER, EMAIL_APP_PASSWORD)
    server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
    server.quit()

    print("✅ Email sent successfully!")

except Exception as e:
    print("❌ Failed to send email:", e)