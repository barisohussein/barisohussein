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
url ="https://www.brooksrunning.com/en_us/mens/shoes/?sz=12&srule=sort_newArrival-descending"
#url = "https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/"
driver.get(url)

wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "a-rating")))

# Scroll to load all products (lazy-loading)
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Scrape all product ratings
rating_divs = driver.find_elements(By.CLASS_NAME, "a-rating")
zero_review_products = []

for i, rating_div in enumerate(rating_divs, start=1):
    # Grab second v--hidden span for rating text
    spans = rating_div.find_elements(By.CLASS_NAME, "v--hidden")
    rating_text = spans[1].text.strip() if len(spans) >= 2 else "No rating"

    # Grab product name
    try:
        product_name = rating_div.find_element(By.XPATH, "./ancestor::li//a[@title]").get_attribute("title").strip()
    except:
        product_name = f"Product {i}"

    print(f"{product_name} — {rating_text}")

    # Check for 0 reviews
    if "0 reviews" in rating_text.lower():
        zero_review_products.append(f"{product_name} — {rating_text}")

driver.quit()

# Send alert email if any products have 0 reviews
if zero_review_products:
    subject = "[Alert] Products with 0 Reviews Detected"
    body = "The following products have 0 reviews:\n\n" + "\n".join(zero_review_products)
    send_email(subject, body)
    print("\n🚨 Email sent for products with 0 reviews.")
else:
    print("\n✅ All products have reviews. No email sent.")
