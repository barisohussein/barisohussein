from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import json
import smtplib
from email.mime.text import MIMEText

# --- Email function same as ratings ---
def send_email(subject, body):
    sender = os.environ['EMAIL_CAMRY']
    password = os.environ['EMAIL_CAMRY_PASSWORD']
    recipient = os.environ['EMAIL_CAMRY']
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, [recipient], msg.as_string())

# --- Selenium setup ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

driver.get("https://www.dwtoyotalasvegas.com/used-vehicles/?make=Toyota&model=Camry")
wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.ID, "srp-results")))

# --- Scrape listings ---
listings_divs = driver.find_elements(By.CSS_SELECTOR, "#srp-results .listing")
listings = set()

for div in listings_divs:
    url = div.get_attribute("data-ag-vdp-url")
    listings.add(url)
    print(url)

driver.quit()

# --- Compare with known listings and send alert ---
DATA_FILE = "car/known_listings.json"
os.makedirs("car", exist_ok=True)

try:
    with open(DATA_FILE, "r") as f:
        known = set(json.load(f))
except:
    known = set()

new_listings = listings - known

if new_listings:
    print(f"Found {len(new_listings)} new listings!")
    send_email(f"New Camry Listings ({len(new_listings)})", "\n".join(new_listings))
    with open(DATA_FILE, "w") as f:
        json.dump(list(listings), f, indent=2)
else:
    print("No new listings.")
