#Will need to enter you're own credentials
#Was able to test with old post, can not guarantee it will work when new post is made
#As of May 2026 5 second loops are the least amount of time to avoid a cloudfare captcha.
#If this changes, the loop will have to be altered 
#Cloudfare may still ban you, then the script reverts to 5 minutes
#Cloudfare may still ban that, so I added the same code with a proxy rotator. We all know how reliable public proxies are though.


import time
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# --- CONFIGURATION ---
# Twilio Credentials (Get these from your Twilio Console dashboard)
TWILIO_SID = "REPLACE_WITH_YOUR_ACCOUNT_SID"
TW_AUTH_TOKEN = "REPLACE_WITH_YOUR_AUTH_TOKEN"
FROM_NUMBER = "REPLACE_WITH_YOUR_TWILIO_PHONE_NUMBER"
TO_NUMBER = "REPLACE_WITH_YOUR_VERIFIED_RECEIVING_NUMBER"

# Target URL
TARGET_URL = "https://hindenburgresearch.com/"

# Global variable to track the last seen article title
last_seen_title = None

def send_text(message_body):
    """Sends an SMS alert via Twilio."""
    try:
        client = Client(TWILIO_SID, TW_AUTH_TOKEN)
        client.messages.create(
            body=message_body,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        print("SMS Alert sent successfully!")
    except Exception as e:
        print(f"Twilio SMS Error: {e}")

def check_for_new_post():
    """Scrapes the website homepage and checks for the newest title."""
    global last_seen_title
    
    # Use standard browser headers to avoid being blocked by simple bot detectors
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Hindenburg's reports are wrapped in <h2> tags on the homepage feed
        latest_post = soup.find("h2")
        if not latest_post:
            print("Could not find any post headers on the page structure.")
            return
            
        # Extract and clean up the text inside the first <h2> tag
        current_title = latest_post.get_text(strip=True)

        # First run initializes the state so you don't text yourself the current old report
        if last_seen_title is None:
            last_seen_title = current_title
            print(f"Monitoring started successfully. Current latest post: '{current_title}'")
            return

        # If the title changes, a new report has dropped
        if current_title != last_seen_title:
            last_seen_title = current_title
            alert_message = f"🚨 NEW HINDENBURG POST:\n\n{current_title}"
            print(f"New post detected! Sending text: {current_title}")
            send_text(alert_message)
        else:
            print("Checked. No new updates found.")

    except Exception as e:
        print(f"Error checking website: {e}")

# Continuous monitoring loop
if __name__ == "__main__":
    # Checks the site every 5 minutes (300 seconds) to avoid getting your IP banned for spamming requests
    CHECK_INTERVAL = 300 
    
    while True:
        check_for_new_post()
        time.sleep(CHECK_INTERVAL)
