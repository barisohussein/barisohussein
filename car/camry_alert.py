import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

URL = "https://www.dwtoyotalasvegas.com/used-vehicles/?make=Toyota&model=Camry"

# Folder where JSON is stored
DATA_FOLDER = "car"
DATA_FILE = os.path.join(DATA_FOLDER, "known_listings.json")

# Ensure the folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

# Load known listings from file
def load_known_listings():
    # If file doesn't exist, create an empty one
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

    # Load safely
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return set(data)
    except:
        return set()

# Save listings back to file
def save_known_listings(listings):
    with open(DATA_FILE, "w") as f:
        json.dump(list(listings), f, indent=2)

# Send alert email or SMS
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


# Scrape the page for listings
def fetch_listings():
    print("\nScraping website...\n")
    response = requests.get(URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    listings = set()

    # Correct selector
    cars = soup.select("div.vehicle-card")

    print(f"Found {len(cars)} vehicles on the page.\n")

    for idx, car in enumerate(cars, start=1):
        title = car.select_one("h2.vehicle-card__title")
        price = car.select_one("span.vehicle-card__price")
        link = car.select_one("a.vehicle-card-link")

        title = title.get_text(strip=True) if title else "Unknown"
        price = price.get_text(strip=True) if price else "Unknown"
        url = "https://www.dwtoyotalasvegas.com" + link["href"] if link else ""

        print(f"--- Listing #{idx} ---")
        print(f"Title: {title}")
        print(f"Price: {price}")
        print(f"URL: {url}\n")

        if url:
            listings.add(url)

    return listings


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
