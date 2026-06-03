#pip install cloudscraper twilio beautifulsoup4 requests

import time
import random
import requests
import cloudscraper
from bs4 import BeautifulSoup
from twilio.rest import Client

# --- CONFIGURATION ---
TWILIO_SID = "REPLACE_WITH_YOUR_ACCOUNT_SID"
TW_AUTH_TOKEN = "REPLACE_WITH_YOUR_AUTH_TOKEN"
FROM_NUMBER = "REPLACE_WITH_YOUR_TWILIO_PHONE_NUMBER"
TO_NUMBER = "REPLACE_WITH_YOUR_VERIFIED_RECEIVING_NUMBER"

TARGET_URL = "https://hindenburgresearch.com"
last_seen_title = None

# Initialize cloudscraper
scraper = cloudscraper.create_scraper()

def get_free_proxies():
    """Fetches a list of fresh, active HTTP proxies from ProxyScrape API."""
    print("Fetching fresh proxy pool...")
    url = "https://proxyscrape.com"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Split the text response into a list of individual IP:PORT strings
            proxies = response.text.strip().split("\r\n")
            print(f"Loaded {len(proxies)} proxies into rotation pool.")
            return proxies
    except Exception as e:
        print(f"Failed to fetch proxy list: {e}")
    return []

def send_text(message_body):
    """Sends an SMS alert via Twilio."""
    try:
        client = Client(TWILIO_SID, TW_AUTH_TOKEN)
        client.messages.create(body=message_body, from_=FROM_NUMBER, to=TO_NUMBER)
        print("SMS Alert sent successfully!")
    except Exception as e:
        print(f"Twilio SMS Error: {e}")

def check_for_new_post(proxy_pool):
    """Scrapes the website using a randomly chosen proxy from the pool."""
    global last_seen_title
    
    if not proxy_pool:
        print("Proxy pool is empty. Skipping this check cycle.")
        return

    # Pick a random proxy and format it for the request
    random_proxy = random.choice(proxy_pool)
    proxy_dict = {
        "http": f"http://{random_proxy}",
        "https": f"http://{random_proxy}"
    }
    
    try:
        # Pass the formatted proxy into the cloudscraper request
        response = scraper.get(TARGET_URL, proxies=proxy_dict, timeout=7)
        
        if response.status_code == 403:
            print(f"Proxy {random_proxy} was blocked by Cloudflare. Trying another next turn.")
            return
        elif response.status_code != 200:
            print(f"Proxy {random_proxy} returned status code: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.content, "html.parser")
        latest_post = soup.find("h2")
        
        if not latest_post:
            return
            
        current_title = latest_post.get_text(strip=True)

        if last_seen_title is None:
            last_seen_title = current_title
            print(f"Monitoring started via proxies. Latest title: '{current_title}'")
            return

        if current_title != last_seen_title:
            last_seen_title = current_title
            alert_message = f"🚨 NEW HINDENBURG POST:\n\n{current_title}"
            print(f"New post detected! Sending text: {current_title}")
            send_text(alert_message)
        else:
            print(f"Checked using proxy {random_proxy}. No updates.")

    except Exception:
        # Free proxies fail often; pass silently and let the loop try a different proxy
        print(f"Proxy {random_proxy} timed out or failed connection.")

if __name__ == "__main__":
    CHECK_INTERVAL = 5 
    
    # Initialize the proxy pool
    proxies = get_free_proxies()
    
    # Refresh the proxy list pool every 15 minutes (180 loops)
    loop_count = 0
    
    print("Starting 5-second loop with rotation...")
    while True:
        # Refresh proxies if pool is exhausted or every 180 iterations
        if not proxies or loop_count >= 180:
            proxies = get_free_proxies()
            loop_count = 0
            
        check_for_new_post(proxies)
        loop_count += 1
        time.sleep(CHECK_INTERVAL)
