from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import smtplib
from email.mime.text import MIMEText

# ---------------- Email function ----------------
def send_email(subject, body):
    sender = os.environ['EMAIL_USERNAME']
    password = os.environ['EMAIL_PASSWORD']
    recipient = os.environ['EMAIL_RECIPIENT']
    cc_recipient = os.environ.get('CC_RECIPIENT')

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    if cc_recipient:
        msg["Cc"] = cc_recipient

    recipients = [recipient]
    if cc_recipient:
        recipients.append(cc_recipient)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, recipients, msg.as_string())

# ---------------- Selenium scraping ----------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

url = "https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/"
driver.get(url)

wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "a-rating")))

# Ensure page fully loads
time.sleep(3)

# Grab the first product's rating div
first_rating_div = driver.find_element(By.CLASS_NAME, "a-rating")

# Extract rating text (second v--hidden span)
spans = first_rating_div.find_elements(By.CLASS_NAME, "v--hidden")
rating_text = spans[1].text.strip() if len(spans) >= 2 else "No rating"

# Grab product name
try:
    product_name = first_rating_div.find_element(
        By.XPATH, "./ancestor::li//a[@title]"
    ).get_attribute("title").strip()
except:
    product_name = "First Product"

print(f"{product_name} — {rating_text}")

driver.quit()

import re
import re

# ---------------- Check only the first product ----------------
# Extract number of reviews safely from rating_text
match = re.search(r"(\d+)\s+reviews", rating_text.lower())
num_reviews = int(match.group(1)) if match else -1

if num_reviews == 0:
    subject = "[Alert] First Product Has 0 Reviews"
    body = f"The first product on the page has 0 reviews:\n\n{product_name} — {rating_text}"
    # Send email
    send_email(subject, body)
    print(f"\n🚨 Email sent: first product has 0 reviews.\n{product_name} — {rating_text}")
else:
    print(f"\n✅ First product has {num_reviews if num_reviews >= 0 else 'unknown'} reviews. No email sent.\n{product_name} — {rating_text}")


