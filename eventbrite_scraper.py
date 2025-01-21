import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Path to Microsoft Edge WebDriver
EDGE_DRIVER_PATH = r"C:\edgedriver_win64\msedgedriver.exe"

# Base Eventbrite URL
BASE_URL = "https://www.eventbrite.com/d/united-states/events--this-month/mezal-or-sotol-or-baconora-or-pulque-or-tequila/?page={}&cur=USD"

# Set up Selenium WebDriver for Edge
options = webdriver.EdgeOptions()
options.use_chromium = True
# options.add_argument("--headless")  # Remove for debugging
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

def scrape_eventbrite_page(page_number):
    service = Service(EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=options)
    
    url = BASE_URL.format(page_number)
    print(f"Scraping page {page_number}: {url}")
    driver.get(url)
    
    wait = WebDriverWait(driver, 20)  # Increase wait time

    try:
        # Scroll multiple times to trigger lazy loading
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)

        # Wait for event elements to load
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li div[data-testid='search-event']")))

        events_data = []
        event_cards = driver.find_elements(By.CSS_SELECTOR, "li div[data-testid='search-event']")

        for event in event_cards:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", event)
                time.sleep(1)

                # Debugging: Print full event block to analyze missing data
                print(event.get_attribute('outerHTML'))

                # Extract event title using JavaScript to handle dynamic rendering
                try:
                    title_element = event.find_element(By.CSS_SELECTOR, "a.event-card-link h3")
                    title = driver.execute_script("return arguments[0].innerText;", title_element).strip()
                except:
                    title = "No Title"

                # Extract event URL
                url = event.find_element(By.CSS_SELECTOR, "a.event-card-link").get_attribute('href')

                # Extract event date using JavaScript for dynamic content
                try:
                    date_element = event.find_element(By.CSS_SELECTOR, "p.Typography_body-md-bold__487rx")
                    date = driver.execute_script("return arguments[0].innerText;", date_element).strip()
                except:
                    date = "No Date Found"

                # Extract event location
                try:
                    location = event.find_elements(By.CSS_SELECTOR, "p.Typography_body-md__487rx")[-1].text.strip()
                except:
                    location = "No Location"

                # Extract event price
                try:
                    price_element = event.find_element(By.XPATH, ".//div[contains(@class, 'priceWrapper')]//p")
                    price = driver.execute_script("return arguments[0].innerText;", price_element).strip()
                except:
                    price = "Free or Unlisted"

                event_data = {
                    'Title': title,
                    'URL': url,
                    'Date': date,
                    'Location': location,
                    'Price': price
                }

                print(event_data)  # Debugging output
                events_data.append(event_data)

            except Exception as e:
                print(f"Error extracting event data: {e}")

    except Exception as e:
        print(f"Error fetching event data: {e}")

    driver.quit()
    return events_data

# Function to scrape multiple pages
def scrape_multiple_pages(total_pages):
    all_events = []
    for page in range(1, total_pages + 1):
        events = scrape_eventbrite_page(page)
        all_events.extend(events)
    return all_events

# Scrape first 3 pages (modify as needed)
total_pages_to_scrape = 341
event_list = scrape_multiple_pages(total_pages_to_scrape)

# Save the results to a CSV file
if event_list:
    df = pd.DataFrame(event_list)
    df.to_csv('eventbrite_events_edge_fixed.csv', index=False)
    print("Data successfully saved to 'eventbrite_events_edge_fixed.csv'")
else:
    print("No events found or failed to scrape data.")
