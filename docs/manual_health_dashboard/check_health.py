#!/usr/bin/env python3
"""
Brooks DPO — Website Health Monitor
Simple version optimized for GitHub Actions
"""

import csv
import os
import time
import yaml
from datetime import datetime, timezone

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

RESULTS_FILE = "docs/manual_health_dashboard/results.csv"
URLS_FILE = "docs/manual_health_dashboard/urls.yaml"

HEADERS = [
    "timestamp",
    "name",
    "url",
    "status",
    "response_time_ms",
    "error"
]


def load_urls():
    with open(URLS_FILE) as f:
        return yaml.safe_load(f)["urls"]


def make_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    return driver


def check_url(driver, entry):

    start = time.time()

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "name": entry["name"],
        "url": entry["url"],
        "status": "DOWN",
        "response_time_ms": "",
        "error": ""
    }

    try:

        driver.get(entry["url"])

        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        elapsed = int((time.time() - start) * 1000)

        result["response_time_ms"] = elapsed
        result["status"] = "UP"

    except Exception as e:

        result["error"] = str(e)[:120]

    return result


def ensure_csv():

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)

    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()


def main():

    ensure_csv()

    urls = load_urls()

    print(f"Checking {len(urls)} URLs...\n")

    driver = make_driver()

    results = []

    try:

        for entry in urls:

            print(f"→ {entry['name']}")

            r = check_url(driver, entry)

            results.append(r)

            print(
                f"  {r['status']} | {r['response_time_ms']}ms {r['error']}"
            )

    finally:

        driver.quit()

    with open(RESULTS_FILE, "a", newline="") as f:

        writer = csv.DictWriter(f, fieldnames=HEADERS)

        for r in results:
            writer.writerow(r)

    up = sum(1 for r in results if r["status"] == "UP")

    print(f"\n{up}/{len(results)} healthy")


if __name__ == "__main__":
    main()