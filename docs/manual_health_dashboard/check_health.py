#!/usr/bin/env python3
"""
Brooks DPO — Website Health Monitor
Runs in GitHub Actions with headless Chrome
"""

import csv
import os
import time
import yaml
import json
from datetime import datetime, timezone

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


RESULTS_FILE = "docs/manual_health_dashboard/results.csv"
URLS_FILE = "docs/manual_health_dashboard/urls.yaml"

HEADERS = [
    "timestamp",
    "name",
    "url",
    "page_type",
    "status_code",
    "response_time_ms",
    "is_up",
    "keywords_checked",
    "keywords_passed",
    "keywords_failed",
    "error",
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

    return webdriver.Chrome(options=options)

def check_selector(driver, selector):

    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)

        if element.is_displayed():
            return True, ""

        return False, "Element found but not visible"

    except Exception as e:
        return False, str(e)
        
def check_search(driver):

    try:

        search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search']")

        search_box.clear()
        search_box.send_keys("ghost")
        search_box.submit()

        WebDriverWait(driver, 10).until(
            lambda d: "ghost" in d.page_source.lower()
        )

        return True, ""

    except Exception as e:
        return False, str(e)[:120]


def check_add_to_cart(driver):

    try:

        button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        if button.is_displayed():
            return True, ""

        return False, "Add to cart missing"

    except Exception as e:
        return False, str(e)[:120]


def check_url(driver, entry):

    url = entry["url"]
    keywords = entry.get("keywords", [])

    result = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "name": entry["name"],
        "url": url,
        "page_type": entry.get("page_type", ""),
        "status_code": "",
        "response_time_ms": "",
        "is_up": "false",
        "keywords_checked": json.dumps(keywords),
        "keywords_passed": "[]",
        "keywords_failed": "[]",
        "error": "",
    }

    start = time.time()

    try:

        driver.get(url)

        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        elapsed = int((time.time() - start) * 1000)

        result["response_time_ms"] = elapsed
        result["status_code"] = 200

        page = driver.page_source.lower()

        passed = [k for k in keywords if k.lower() in page]
        failed = [k for k in keywords if k.lower() not in page]

        result["keywords_passed"] = json.dumps(passed)
        result["keywords_failed"] = json.dumps(failed)

        result["is_up"] = "true" if not failed else "false"

        if failed:
            result["error"] = f"Missing keywords: {', '.join(failed)}"

        page_type = entry.get("page_type")

        if page_type == "SHOEFINDER":

            ok, err = check_shoefinder(driver)

            if not ok:
                result["is_up"] = "false"
                result["error"] = f"ShoeFinder failed: {err}"

        if page_type == "SEARCH":

            ok, err = check_search(driver)

            if not ok:
                result["is_up"] = "false"
                result["error"] = f"Search failed: {err}"

        if page_type == "PDP":

            ok, err = check_add_to_cart(driver)

            if not ok:
                result["is_up"] = "false"
                result["error"] = f"Add-to-cart failed: {err}"

    except Exception as e:

        result["status_code"] = 500
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
                f"{'UP' if r['is_up']=='true' else 'DOWN'} "
                f"[{r['response_time_ms']}ms] {r['error']}"
            )

    finally:

        driver.quit()

    with open(RESULTS_FILE, "a", newline="") as f:

        writer = csv.DictWriter(f, fieldnames=HEADERS)

        for r in results:
            writer.writerow(r)

    up = sum(1 for r in results if r["is_up"] == "true")

    print(f"\n{up}/{len(results)} healthy")


if __name__ == "__main__":
    main()
