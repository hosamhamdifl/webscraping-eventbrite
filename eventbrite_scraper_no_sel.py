import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Base Eventbrite URL with pagination
BASE_URL = "https://www.eventbrite.com/d/united-states/events--this-month/mezal-or-sotol-or-baconora-or-pulque-or-tequila/?page={}&cur=USD"

# Headers to mimic a real browser request to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Output CSV filename
OUTPUT_CSV = "eventbrite_event_urls.csv"

def scrape_eventbrite_page(page_number):
    """Scrape event URLs from a single page using requests and BeautifulSoup."""
    url = BASE_URL.format(page_number)
    print(f"Scraping page {page_number}: {url}")

    try:
        # Fetch page content
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        # Check for request success
        if response.status_code != 200:
            print(f"Failed to fetch page {page_number}, Status Code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all event links using 'a' tags with class 'event-card-link'
        event_links = soup.select("a.event-card-link")
        urls = []

        for link in event_links:
            event_url = link.get("href")
            if event_url and "eventbrite.com/e/" in event_url:
                urls.append({'URL': event_url})

        print(f"Found {len(urls)} event URLs on page {page_number}")
        return urls

    except Exception as e:
        print(f"Error scraping page {page_number}: {e}")
        return []

def scrape_multiple_pages(total_pages):
    """Scrape multiple pages for event URLs."""
    all_event_urls = []

    for page in range(1, total_pages + 1):
        urls = scrape_eventbrite_page(page)
        all_event_urls.extend(urls)

        # Add delay to avoid rate limiting
        time.sleep(2)

    return all_event_urls

# Number of pages to scrape
total_pages_to_scrape = 341

# Run scraper
event_list = scrape_multiple_pages(total_pages_to_scrape)

# Save results to CSV
if event_list:
    df = pd.DataFrame(event_list)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Data successfully saved to '{OUTPUT_CSV}'")
else:
    print("No event URLs found.")
