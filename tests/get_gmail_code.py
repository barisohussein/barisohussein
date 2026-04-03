# save as get_gmail_code.py
import imaplib
import email
import re
import os


EMAIL_USER = "barisobrooks@gmail.com"
EMAIL_PASS = os.environ["EMAIL_APP_PASSWORD"]


def get_latest_code():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        if not mail_ids:
            return None

        latest_email_id = mail_ids[-1]
        status, data = mail.fetch(latest_email_id, "(RFC822)")

        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                code_match = re.search(r'\b\d{4,8}\b', body)
                if code_match:
                    return code_match.group(0)

        mail.close()
        mail.logout()
        return None
    except Exception as e:
        return None

if __name__ == "__main__":
    code = get_latest_code()
    if code:
        print(code)