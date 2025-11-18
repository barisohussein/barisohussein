import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

URL = "https://www.dwtoyotalasvegas.com/used-vehicles/?make=Toyota&model=Camry"
DATA_FILE = "known_listings.json"

# Load known listings from file
def load_known_listings():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return set(json.load(f))
    return set()

# Save listings back to file
def save_known_listings(listings):
    with open(DATA_FILE, "w") as f:
        json.dump(list(listings), f)

# Send alert email or SMS
def send_alert(new_listings):
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    receiver = os.environ["EMAIL_RECEIVER"]

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
    response = requests.get(URL, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    listings = set()

    # Find each listing card by CSS class
    cars = soup.select(".vehicle-card")  # may need adjustment based on site HTML
    
    for car in cars:
        link = car.find("a", href=True)
        if link:
            full_url = "https://www.dwtoyotalasvegas.com" + link["href"]
            listings.add(full_url)

    return listings


# Main program
def main():
    print("Checking for new Camry listings...")

    known = load_known_listings()
    current = fetch_listings()

    new_listings = current - known

    if new_listings:
        print(f"Found {len(new_listings)} new listings!")
        send_alert(new_listings)
        save_known_listings(current)
    else:
        print("No new listings.")

if __name__ == "__main__":
    main()
