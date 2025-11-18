import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.dwtoyotalasvegas.com/used-vehicles/?make=Toyota&model=Camry"
DATA_FOLDER = "car"
DATA_FILE = os.path.join(DATA_FOLDER, "known_listings.json")

os.makedirs(DATA_FOLDER, exist_ok=True)

# Load known listings
def load_known_listings():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(DATA_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

# Save listings
def save_known_listings(listings):
    with open(DATA_FILE, "w") as f:
        json.dump(list(listings), f, indent=2)

# Send alert email
def send_alert(new_listings):
    sender = os.environ["EMAIL_USERNAME"]
    password = os.environ["EMAIL_PASSWORD"]
    receiver = os.environ["EMAIL_RECIPIENT"]

    subject = f"🚗 New Camry Listing Found ({len(new_listings)})"
    body = "New Toyota Camry listings:\n\n" + "\n".join(new_listings)

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

    print("Alert sent!")

# Scrape the page with Selenium
def fetch_listings():
    print("\nLoading page with Selenium...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(URL)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "srp-results")))

        listings_divs = driver.find_elements(By.CSS_SELECTOR, "#srp-results .listing")
        print(f"Found {len(listings_divs)} listings\n")

        listings = set()

        for idx, div in enumerate(listings_divs, start=1):
            url = div.get_attribute("data-ag-vdp-url")
            title = div.get_attribute("data-vehicle-make-model")
            price = div.get_attribute("data-vehicle-price")
            trim = div.get_attribute("data-ag-trim")

            listings.add(url)

            print(f"--- Listing #{idx} ---")
            print(f"Title: {title}")
            print(f"Price: {price}")
            print(f"Trim: {trim}")
            print(f"URL: {url}\n")

        return listings

    finally:
        driver.quit()

def main():
    print("Checking for new Camry listings...\n")

    known = load_known_listings()
    current = fetch_listings()

    new_listings = current - known

    if new_listings:
        print(f"\n🔥 Found {len(new_listings)} NEW listings!")
        for nl in new_listings:
            print("NEW:", nl)

        send_alert(new_listings)
        save_known_listings(current)
    else:
        print("No new listings.\n")

if __name__ == "__main__":
    main()
