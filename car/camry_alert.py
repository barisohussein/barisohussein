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
import time

# --- Email function ---
def send_email(subject, body):
    sender = "barisobrooks@gmail.com"
    password = os.environ['EMAIL_CAMRY_PASSWORD']
    recipient = "barisobrooks@gmail.com"
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

URL = "https://www.dwtoyotalasvegas.com/used-vehicles/?make=Toyota&model=Camry"
driver.get(URL)

wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.ID, "srp-results")))
time.sleep(3)  # allow full page load

listings_divs = driver.find_elements(By.CSS_SELECTOR, "#srp-results .listing")

# --- Full listings with details ---
full_listings = []
urls = set()

for div in listings_divs:
    listing = {
        "vehicle_id": div.get_attribute("data-vehicle-id"),
        "vin": div.get_attribute("data-vehicle-vin"),
        "condition": div.get_attribute("data-vehicle-condition"),
        "year": div.get_attribute("data-vehicle-year"),
        "stock_number": div.get_attribute("data-vehicle-stock-number"),
        "make_model": div.get_attribute("data-vehicle-make-model"),
        "price": div.get_attribute("data-vehicle-price"),
        "discount": div.get_attribute("data-vehicle-discount"),
        "dealer": div.get_attribute("data-dealer-name"),
        "exterior_color": div.get_attribute("data-exteriorColor"),
        "body_type": div.get_attribute("data-ag-type"),
        "trim": div.get_attribute("data-ag-trim"),
        "vdp_url": div.get_attribute("data-ag-vdp-url")
    }
    full_listings.append(listing)
    urls.add(listing["vdp_url"])
    print(listing["vdp_url"])

driver.quit()

# --- Save full listings ---
os.makedirs("car", exist_ok=True)
FULL_FILE = "car/full_listings.json"
with open(FULL_FILE, "w") as f:
    json.dump(full_listings, f, indent=2)
print(f"✅ Saved full listings to {FULL_FILE}")

# --- Save known URLs and detect new ---
KNOWN_FILE = "car/known_listings.json"
try:
    with open(KNOWN_FILE, "r") as f:
        known_urls = set(json.load(f))
except:
    known_urls = set()

new_listings = urls - known_urls

if new_listings:
    print(f"🔥 Found {len(new_listings)} new listings!")
    send_email(
        f"New Camry Listings ({len(new_listings)})",
        "\n".join(new_listings)
    )

# --- Save current URLs ---
with open(KNOWN_FILE, "w") as f:
    json.dump(list(urls), f, indent=2)
print(f"✅ Saved known URLs to {KNOWN_FILE}")
