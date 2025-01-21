import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Input CSV file containing event URLs
INPUT_CSV = "eventbrite_event_urls.csv"
OUTPUT_CSV = "eventbrite_event_details_with_location.csv"

# Headers to mimic a real browser request to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_event_details(event_url):
    """Scrape event details including full location text."""
    try:
        print(f"Scraping event: {event_url}")

        # Send GET request to fetch page content
        response = requests.get(event_url, headers=HEADERS, timeout=15)
        
        # Check for request success
        if response.status_code != 200:
            print(f"Failed to fetch {event_url}, status code: {response.status_code}")
            return {'URL': event_url, 'Title': 'Error', 'Date': 'Error', 'Location': 'Error', 'About': 'Error'}

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract event title
        try:
            title = soup.select_one("div.event-details__main-inner h1.event-title").text.strip()
        except AttributeError:
            title = "No Title Found"

        # Extract event date
        try:
            date = soup.select_one("div[data-testid='display-date-container'] span.date-info__full-datetime").text.strip()
        except AttributeError:
            date = "No Date Found"

        # Extract full location (inside and after <p> tag)
        try:
            location_div = soup.select_one("div.location-info__address")
            if location_div:
                location = " ".join(location_div.stripped_strings)  # Get all text inside div, including outside <p>
            else:
                location = "No Location Found"
        except AttributeError:
            location = "No Location Found"

        # Extract "About" section
        try:
            about_section = soup.select_one("div.eds-text--left")
            about = about_section.get_text(separator=" ").strip() if about_section else "No About Info Found"
        except AttributeError:
            about = "No About Info Found"

        event_data = {
            'URL': event_url,
            'Title': title,
            'Date': date,
            'Location': location,
            'About': about
        }

        print(event_data)  # Debugging output
        return event_data

    except Exception as e:
        print(f"Error scraping {event_url}: {e}")
        return {'URL': event_url, 'Title': 'Error', 'Date': 'Error', 'Location': 'Error', 'About': 'Error'}


def scrape_all_events():
    """Read event URLs from CSV and scrape details for each."""
    df = pd.read_csv(INPUT_CSV)
    events_data = []

    # Iterate through each event URL in the CSV
    for index, row in df.iterrows():
        event_url = row['URL']
        event_info = scrape_event_details(event_url)
        events_data.append(event_info)

    # Save to CSV
    output_df = pd.DataFrame(events_data)
    output_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Data successfully saved to '{OUTPUT_CSV}'")


# Run the scraper
scrape_all_events()
