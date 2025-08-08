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
    cc_recipient = os.environ.get('CC_RECIPIENT')  # Optional CC address

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg["Cc"] = cc_recipient

    # Build list of all recipients for sending
    recipients = [recipient]
    if cc_recipient:
        recipients.append(cc_recipient)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, recipients, msg.as_string())


def main():
    sitemap_index_url = "https://www.brooksrunning.com/sitemap_index.xml"
    filters = ['category'] #, 'shoes', 'womens', 'mens', 'product']

    manual_urls = {
        "https://www.brooksrunning.com/en_us/featured/unisex-running-shoes/hyperion-elite-5/100049.html",
        "https://www.brooksrunning.com/en_us/featured/accessories/journey-hat/280530.html",
        "https://www.brooksrunning.com/en_us/mens/",
        "https://www.brooksrunning.com/en_us/sale/mens/shoes/",
        "https://www.brooksrunning.com/en_us/featured/ghost/mens/",
        "https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/ghost-max-2/110431.html?dwvar_110431_color=125",
        'https://www.brooksrunning.com/en_us',
        'https://www.brooksrunning.com/en_us/shoefinder/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-max-2/120420.html?dwvar_120420_color=190',
        'https://www.brooksrunning.com/en_us/shopping-cart/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/adrenaline-gts-24/120426.html?dwvar_120426_color=181',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-17/120431.html?dwvar_120431_color=105',
        'https://www.brooksrunning.com/en_us/womens/shoes/',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/adrenaline-gts-24/110437.html?dwvar_110437_color=423',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/glycerin-22/120434.html?dwvar_120434_color=897',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-16/120407.html?dwvar_120407_color=175',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-max-3/120457.html?dwvar_120457_color=151',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/ghost-17/110442.html?dwvar_110442_color=048',
        'https://www.brooksrunning.com/on/demandware.store/Sites-BrooksRunning-Site/en_US/ShoeFinder-Show',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/glycerin-22/110445.html?dwvar_110445_color=135',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/ghost-max-2/110431.html?dwvar_110431_color=125',
        'https://www.brooksrunning.com/en_us/mens/shoes/',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/ghost-max-3/110464.html?dwvar_110464_color=162',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/glycerin-max/120436.html?dwvar_120436_color=447',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/ghost-16/110418.html?dwvar_110418_color=040',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/glycerin-gts-22/120435.html?dwvar_120435_color=429',
        'https://www.brooksrunning.com/en_us/womens/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/glycerin-22/120434.html?dwvar_120434_color=110',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-17/120431.html',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/glycerin-gts-22/110446.html?dwvar_110446_color=135',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/glycerin-max/110447.html?dwvar_110447_color=099',
        'https://www.brooksrunning.com/en_us/check-out/check-out-process/?stage=shipping#shipping',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/glycerin-22/120434.html',
        'https://www.brooksrunning.com/en_us/mens/',
        'https://www.brooksrunning.com/en_us/womens/shoes/walking-shoes/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-max-2/120420.html',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/revel-7/120424.html?dwvar_120424_color=522',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/adrenaline-gts-24/120426.html',
        'https://www.brooksrunning.com/en_us/sale/womens/shoes/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/glycerin-gts-22/120435.html',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/glycerin-stealthfit-22/120437.html?dwvar_120437_color=135',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/adrenaline-gts-24/120426.html?dwvar_120426_color=126',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/launch-11/120439.html?dwvar_120439_color=164',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/ghost-17/110442.html',
        'https://www.brooksrunning.com/en_us/check-out/account-login/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-max-3/120457.html?tid=PSOC%3AMeta%3AGhostMax3%3AGhostMax3_ConversionsSales_2025%3APerformance%3AUSA%3AMixed_GM3ConsolidatedAudience_GN_ConversionNumber_Hone%3AImage_Static_GN_007%3A',
        'https://www.brooksrunning.com/en_us/featured/ghost/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-17/120431.html?dwvar_120431_color=458&tid=PSOC%3AMeta%3ATest-Adora-Ghost17%3ATest-Adora-Ghost17_ConversionsSales_2025%3APerformance%3AUSA%3AMixed_PixelSiteVisitorsGhost+LAL_GN_Conve',
        'https://www.brooksrunning.com/en_us/mens/shoes/walking-shoes/',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/revel-7/110435.html?dwvar_110435_color=014',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/launch-11/110450.html?dwvar_110450_color=135',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/glycerin-22/110445.html',
        'https://www.brooksrunning.com/en_us/sale/mens/shoes/',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/ghost-max-2/110431.html',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/beast-gts-24/110425.html?dwvar_110425_color=452',
        'https://www.brooksrunning.com/en_us/sale/',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/glycerin-max/110447.html?dwvar_110447_color=303',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/adrenaline-gts-24/110437.html',
        'https://www.brooksrunning.com/en_us/featured/glycerin/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/revel-8/120456.html?dwvar_120456_color=171',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ariel-gts-24/120414.html?dwvar_120414_color=080',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/glycerin-gts-22/110446.html',
        'https://www.brooksrunning.com/en_us/mens/shoes/trail-shoes/cascadia-19/110457.html?dwvar_110457_color=722',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-16/120407.html?tid=em:st:USA%7C20250803_Ghost_16_Last_Call_Sale_Email_Resend_2%7CCV3X:Dont_miss_the_Ghost_16_at_29_off:August_03_2025',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/glycerin-stealthfit-22/110448.html?dwvar_110448_color=072',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/trace-4/120441.html?dwvar_120441_color=198',
        'https://www.brooksrunning.com/en_us/womens/shoes/treadmill-shoes/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-17/120431.html?tid=PSOC%3AMeta%3AGhost-17%3AGhost-17_Traffic_2025%3APerformance%3AUSA%3ALAL_AmperityRTBLAL-RunningReputation_GN_LandingPageViews_Resonate%3AImage_Static_Female_AllNe',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-max-3/120457.html?tid=em:st:USA%7C20250801_Gear_Instory_Ghost_Max_3_Launch_Email_Global%7CCV3X:The_new_Ghost_Max_3:August_01_2025:mct_ghostmax3',
        'https://www.brooksrunning.com/en_us/featured/adrenaline-gts/',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-max-3/120457.html?tid=PSOC%3AMeta%3AGhostMax3%3AGhostMax3_ConversionsSales_2025%3APerformance%3AUSA%3ALAL_PixelSiteVisitorsGhostMax_GN_ConversionNumber_Hone%3AImage_Static_GN_007%3A',
        'https://www.brooksrunning.com/en_us/mens/shoes/road-running-shoes/hyperion-max-3/110467.html?dwvar_110467_color=670',
        'https://www.brooksrunning.com/en_us/womens/shoes/road-running-shoes/ghost-max-3/120457.html',
        'https://www.brooksrunning.com/en_us/featured/unisex-running-shoes/hyperion-elite-5/100049.html?dwvar_100049_color=681'
    }
    all_sitemaps = get_sitemap_urls_from_index(sitemap_index_url)
    product_category_sitemaps = [s for s in all_sitemaps if 'product' in s or 'category' in s]

    filtered_urls = get_filtered_urls(product_category_sitemaps, filters)

    all_urls_to_check = filtered_urls.union(manual_urls)
    print(f"\n✅ Total URLs to check (including manual): {len(all_urls_to_check)}")

    broken_urls = get_broken_urls(all_urls_to_check)

    # Only send email if broken URLs exist
    if broken_urls:
        subject = "[Alert] Broken URLs Detected"
        body = "The following URLs returned an error:\n\n"
        for url, status in broken_urls:
            body += f"{url} - {status}\n"

        send_email(subject, body)
        print("\n🚨 Email sent with broken URLs list.")
    else:
        print("\n✅ All URLs are live. No email sent.")

if __name__ == "__main__":
    main()
