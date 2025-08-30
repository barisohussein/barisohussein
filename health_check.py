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


# ---------------- Selenium health check ----------------
def check_brooks_shoes_page():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.set_window_size(1920, 1080)

    url = "https://www.brooksrunning.com/en_us/shoes/"
    driver.get(url)

    expected_elements = [
        {"type": By.CSS_SELECTOR, "value": "label[for='pcp-filter-gender-0']"},  # Women
        {"type": By.CSS_SELECTOR, "value": "label[for='pcp-filter-size_Shoe-0']"},  # Size 5.0
        {"type": By.CSS_SELECTOR, "value": "label[for='pcp-filter-turntoAverageRating-0']"},  # Rating filter
        {"type": By.CSS_SELECTOR, "value": "label[for='pcp-filter-spec_Surface-0']"},  # Road
        {"type": By.CSS_SELECTOR, "value": "img.a-responsive-image__img"},  # Product/visual images
        {"type": By.CSS_SELECTOR, "value": "svg.icon-account-icon"},  # Account icon
        {"type": By.CSS_SELECTOR, "value": "svg.icon-cart-icon"},  # Cart icon
        {"type": By.CLASS_NAME, "value": "a-rating"},  # First rating
        {"type": By.CSS_SELECTOR, "value": "div.m-product-tile__name"},  # Product names
        {"type": By.CSS_SELECTOR, "value": "span.pricing__sale.js-sale-price"},  # Sale price
        {"type": By.CSS_SELECTOR, "value": "img.a-responsive-image__img[data-swatch-id]"},  # Swatch images
        {"type": By.CSS_SELECTOR, "value": "button.js-load-more-button"},  # Load more button
    ]

    errors = []
    wait = WebDriverWait(driver, 15)

    # -------- check expected elements -------- #
    for elem in expected_elements:
        try:
            wait.until(EC.presence_of_element_located((elem["type"], elem["value"])))
        except Exception:
            errors.append(f"Missing element: {elem['value']} ({elem['type']})")

    # -------- check product tiles -------- #
    product_tiles = driver.find_elements(By.CSS_SELECTOR, "div.m-product-tile__name")
    if len(product_tiles) < 12:
        errors.append(f"Only found {len(product_tiles)} product tiles, expected at least 12")

    for i, tile in enumerate(product_tiles, start=1):
        nav_url = tile.get_attribute("data-navigation-url")
        if not nav_url or not nav_url.strip():
            errors.append(f"Product tile {i} missing navigation URL")

    driver.quit()

    # -------- reporting -------- #
    if errors:
        subject = "[ALERT] Brooks /shoes page check FAILED"
        body = f"The Brooks Running shoes page has issues:\n\n" + "\n".join(errors)
        send_email(subject, body)
        print("\n🚨 Issues found. Email sent.")
    else:
        print("\n✅ Brooks Running /shoes page is healthy!")


# ---------------- Run ----------------
if __name__ == "__main__":
    check_brooks_shoes_page()
