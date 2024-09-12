import os
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import logging
from website_urls import GAMERANT_WEBSITE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a requests session with retry mechanism
def requests_retry_session(
    retries=5,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Function to send a request and return a BeautifulSoup object
def get_soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        logging.info(f"Fetching URL: {url}")
        response = requests_retry_session().get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

# Function to extract data from individual event pages
def scrape_event_page(event_url):
    time.sleep(2)  # Add delay between requests to avoid rate-limiting
    soup = get_soup(event_url)
    if soup is None:
        return 'Error', 'Error', 'No Image URL Found'

    try:
        # Extract event title
        title_tag = soup.find('h1', class_='article-header-title')
        event_title = title_tag.get_text(strip=True) if title_tag else 'No title found'

        # Extract event image URL
        div_tag = soup.find('div', class_='heading_image')
        event_image_url = div_tag['data-img-url'] if div_tag and div_tag.has_attr('data-img-url') else 'No image found'

        # Extract event content (first paragraph after content-block-regular)
        content_block = soup.find(class_='content-block-regular')
        first_paragraph = content_block.find('p') if content_block else None
        event_content = first_paragraph.get_text(strip=True) if first_paragraph else 'No content found'
        
        return event_title, event_content, event_image_url
    
    except Exception as e:
        logging.error(f"Error scraping event page {event_url}: {e}")
        return 'Error', 'Error', 'No Image URL Found'

# Function to extract events from the main page
def scrape_main_page(soup):
    target_class = 'display-card scroll-offset article article-card small no-badge active-content'
    excluded_classes = {'side-navigation-social', 'side-navigation-list', 'sidenav-subnav', 'css-menu--target', 'table-content-list'}

    # Find the first element with the target class
    target_element = soup.find(class_=target_class)

    events_data = []

    if target_element:
        previous_siblings = target_element.find_all_previous()
        for sibling in previous_siblings:
            if sibling.name == 'ul' and not any(cls in excluded_classes for cls in (sibling.get('class') or [])):
                li_elements = sibling.find_all('li')
                for li in li_elements:
                    # Extract event date
                    start_date = li.find('strong').get_text(strip=True) if li.find('strong') else 'No date found'

                    if start_date != 'No date found':
                        try:
                            # Try to parse date in the format 'Month Day' (e.g., 'September 3')
                            start_date_obj = datetime.strptime(start_date, '%B %d')
                            
                            # Add the current year if the year is missing in the date string
                            start_date_obj = start_date_obj.replace(year=datetime.now().year)
                            
                            # Add 7 days to start_date
                            end_date_obj = start_date_obj + timedelta(days=7)
                            
                            # Convert end_date back to string in the desired format
                            end_date_str = end_date_obj.strftime('%d-%m-%Y')
                        except ValueError:
                            print(f"Failed to parse date: {start_date}")
                            start_date_obj = None
                            end_date_str = ''
                    else:
                        print("No start date found")
                        start_date = ''
                        end_date_str = ''

                    # Extract event description
                    event_description = li.find('em').get_text(strip=True) if li.find('em') else 'No description found'

                    # Extract event URL
                    event_url = li.find('a')['href'] if li.find('a') else 'No URL found'

                    # Scrape additional data from the event page
                    if event_url != 'No URL found':
                        event_title, event_content, event_image_url = scrape_event_page(event_url)
                    else:
                        event_title, event_content, event_image_url = 'No title found', 'No content found', 'No Image URL Found'

                    # Append the data
                    events_data.append({
                        'Event Name': event_description,
                        "Event Type": "Sale",
                        'Event Description': event_content,
                        "Calendar": "sephora Calendar",
                        "All Day": "No",
                        "Public/Private": "Public",
                        "Reported Count": 0,
                        'Start Date': start_date,
                        "End Date": end_date_str,
                        'Image URL': event_image_url,
                        'Created By': '',
                        'URL': event_url,
                    })
    return events_data

# Function to save events data to CSV in the 'csv_output' folder
def save_to_csv(data, filename='gamerant_website_data.csv'):
    # Define the output folder
    output_folder = 'csv_output'

    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save the CSV file inside the 'csv_output' folder
    file_path = os.path.join(output_folder, filename)
    
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    logging.info(f"The scraped data has been saved to '{file_path}'.")

# Main function to orchestrate the scraping
def scrape_gamerant_events():
    soup = get_soup(GAMERANT_WEBSITE_URL)
    if soup:
        events_data = scrape_main_page(soup)
        save_to_csv(events_data)

# Run the scraper
if __name__ == "__main__":
    scrape_gamerant_events()
