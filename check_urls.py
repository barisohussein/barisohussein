import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

def get_sitemap_urls_from_index(index_url):
    response = requests.get(index_url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'xml')
    return [sitemap.find('loc').text for sitemap in soup.find_all('sitemap')]

def get_urls_from_sitemap(sitemap_url):
    urls = set()
    response = requests.get(sitemap_url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'xml')
    for url in soup.find_all('url'):
        loc = url.find('loc')
        if loc and loc.text:
            urls.add(loc.text)
    return urls

def get_filtered_urls(sitemap_urls, filters):
    filtered_urls = set()
    for sitemap_url in sitemap_urls:
        print(f"Parsing sitemap: {sitemap_url}")
        urls = get_urls_from_sitemap(sitemap_url)
        for url in urls:
            if any(filt in url for filt in filters):
                filtered_urls.add(url)
    return filtered_urls

def get_broken_urls(urls):
    broken = []
    print(f"\nChecking {len(urls)} URLs for status...")
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                broken.append((url, response.status_code))
                print(f"⚠️ {url} returned status code {response.status_code}")
        except Exception as e:
            broken.append((url, str(e)))
            print(f"❌ Error checking {url}: {e}")
    return broken

def send_email(subject, body):
    sender = os.environ['EMAIL_USERNAME']
    password = os.environ['EMAIL_PASSWORD']
    recipient = os.environ['EMAIL_RECIPIENT']

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

def main():
    sitemap_index_url = "https://www.brooksrunning.com/sitemap_index.xml"
    filters = ['category']
    #filters = ['shoes', '.html', 'womens', 'mens', 'product', 'category']

    manual_urls = {
        # Add any URLs you want to check manually here:
        "https://www.brooksrunning.com/en_us/featured/unisex-running-shoes/hyperion-elite-5/100049.html",
        "https://www.brooksrunning.com/en_us/featured/accessories/journey-hat/280530.html",
        "https://www.amazon.com/404"
    }

    all_sitemaps = get_sitemap_urls_from_index(sitemap_index_url)
    product_category_sitemaps = [s for s in all_sitemaps if 'product' in s or 'category' in s]

    filtered_urls = get_filtered_urls(product_category_sitemaps, filters)

    # Combine filtered URLs with manual URLs
    all_urls_to_check = filtered_urls.union(manual_urls)

    print(f"\n✅ Total URLs to check (including manual): {len(all_urls_to_check)}")

    broken_urls = get_broken_urls(all_urls_to_check)

    if broken_urls:
        subject = "[Alert] Broken URLs Detected"
        body = "The following URLs returned an error:\n\n"
        for url, status in broken_urls:
            body += f"{url} - {status}\n"
    else:
        subject = "[Info] All URLs are Live"
        body = "✅ All checked URLs on brooksrunning.com are live and returning HTTP 200."

    send_email(subject, body)
    print("\nEmail sent with the results.")

if __name__ == "__main__":
    main()
