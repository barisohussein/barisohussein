"""
Daily monitor for John L Scott adult-family-home listings.

Scrapes the listings widget on the agent site, compares the current set of
listings against the set saved from the previous run (data/known_listings.json,
committed to the repo by the GitHub Actions workflow), and emails you a
summary if any NEW listings have appeared since last time.

Run manually:
    pip install -r requirements.txt
    playwright install --with-deps chromium
    python check_listings.py
"""

import asyncio
import json
import os
import re
import smtplib
from email.mime.text import MIMEText
from pathlib import Path

from playwright.async_api import async_playwright

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = "https://dougl.johnlscott.com"
LISTINGS_URL = f"{BASE_URL}/adult-family-homes-for-sale"

STATE_FILE = Path(__file__).parent / "data" / "known_listings.json"

MAX_SCROLLS = 20
SCROLL_PAUSE_SECONDS = 1.5
SETTLE_SECONDS = 3


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

def send_email(subject: str, body: str):
    sender = os.environ.get("EMAIL_USERNAME")
    password = os.environ.get("EMAIL_PASSWORD")
    recipient = os.environ.get("EMAIL_RECIPIENT")
    cc_recipient = os.environ.get("CC_RECIPIENT")

    if not sender or not password or not recipient:
        print("Missing required email environment variables. Email not sent.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    if cc_recipient:
        msg["Cc"] = cc_recipient

    recipients = [recipient] + ([cc_recipient] if cc_recipient else [])

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, recipients, msg.as_string())
        print(f"Email sent: {subject}")
    except smtplib.SMTPAuthenticationError as e:
        print("SMTP authentication failed. Check EMAIL_USERNAME / EMAIL_PASSWORD (Gmail App Password).")
        print(str(e))
    except Exception as e:
        print("Failed to send email:", str(e))


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

def parse_specs(specs_text: str) -> dict:
    """'4 Beds 2 Baths 1648 SqFt' -> {'beds': '4', 'baths': '2', 'sqft': '1648'}"""
    beds = re.search(r"([\d.]+)\s*Beds?", specs_text, re.I)
    baths = re.search(r"([\d.]+)\s*Baths?", specs_text, re.I)
    sqft = re.search(r"([\d,]+)\s*SqFt", specs_text, re.I)
    return {
        "beds": beds.group(1) if beds else "",
        "baths": baths.group(1) if baths else "",
        "sqft": sqft.group(1).replace(",", "") if sqft else "",
    }


async def scroll_to_load_all(page):
    last_count = -1
    for _ in range(MAX_SCROLLS):
        count = len(await page.query_selector_all("a[href*='/listing/']"))
        if count == last_count:
            break
        last_count = count
        await page.mouse.wheel(0, 3000)
        await asyncio.sleep(SCROLL_PAUSE_SECONDS)


async def scrape_listings() -> list[dict]:
    listings = []
    seen_links = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        )
        await page.goto(LISTINGS_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(SETTLE_SECONDS)
        await scroll_to_load_all(page)

        anchors = await page.query_selector_all("a[href*='/listing/']")
        for a in anchors:
            href = await a.get_attribute("href")
            if not href:
                continue
            full_link = href if href.startswith("http") else BASE_URL + href
            if full_link in seen_links:
                continue
            seen_links.add(full_link)

            async def text_of(sel):
                el = await a.query_selector(sel)
                return (await el.inner_text()).strip() if el else ""

            status = await text_of(".jls-listing-status")
            location = await text_of(".jls-listing-location")
            price = await text_of(".jls-listing-price")
            specs_text = await text_of(".jls-listing-specs")
            specs = parse_specs(specs_text)

            listings.append({
                "link": full_link,
                "status": status,
                "location": location,
                "price": price,
                "beds": specs["beds"],
                "baths": specs["baths"],
                "sqft": specs["sqft"],
            })

        await browser.close()

    return listings


# ---------------------------------------------------------------------------
# State diffing
# ---------------------------------------------------------------------------

def load_previous_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # keyed by link for easy lookup
        return {item["link"]: item for item in data.get("listings", [])}
    except Exception as e:
        print(f"Could not read previous state file ({e}); treating as empty.")
        return {}


def save_state(listings: list[dict]):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"listings": listings}, f, indent=2)


def format_listing(item: dict) -> str:
    parts = [item["price"] or "Price N/A"]
    if item["beds"] or item["baths"] or item["sqft"]:
        parts.append(
            f"{item['beds']} bd / {item['baths']} ba / {item['sqft']} sqft"
        )
    if item["location"]:
        parts.append(item["location"])
    if item["status"]:
        parts.append(f"[{item['status']}]")
    parts.append(item["link"])
    return " — ".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    previous = load_previous_state()
    current_listings = await scrape_listings()

    if not current_listings:
        print("No listings found on this run — page may have failed to load "
              "or its structure changed. Not overwriting saved state, to "
              "avoid wiping known listings on a transient failure.")
        return

    current_links = {item["link"] for item in current_listings}
    previous_links = set(previous.keys())

    new_links = current_links - previous_links
    new_listings = [item for item in current_listings if item["link"] in new_links]

    print(f"Previously known: {len(previous_links)} | Currently found: {len(current_links)} "
          f"| New: {len(new_listings)}")

    if new_listings:
        body_lines = [f"{len(new_listings)} new adult family home listing(s) found:\n"]
        for item in new_listings:
            body_lines.append(format_listing(item))
        body_lines.append(f"\nFull search: {LISTINGS_URL}")
        body = "\n\n".join(body_lines)

        send_email(
            subject=f"[JLS Alert] {len(new_listings)} new adult family home listing(s)",
            body=body,
        )
    else:
        print("No new listings since last run.")

    save_state(current_listings)


if __name__ == "__main__":
    asyncio.run(main())
