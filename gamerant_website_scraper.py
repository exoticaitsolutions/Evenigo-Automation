import requests
from bs4 import BeautifulSoup
import pandas as pd
from website_urls import GAMERANT_WEBSITE_URL


# Function to send a request and return a BeautifulSoup object
def get_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to extract data from individual event pages
def scrape_event_page(event_url):
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
        print(f"Error scraping event page {event_url}: {e}")
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
                    event_date = li.find('strong').get_text(strip=True) if li.find('strong') else 'No date found'

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
                        'Event Date': event_date,
                        'Event Title': event_description,
                        'Event URL': event_url,
                        'Event Page Title': event_title,
                        'Event Page Image URL': event_image_url,
                        'Event Page Content': event_content,
                        'Created By': 'test@gmail.com'
                    })
    return events_data

# Function to save events data to CSV
def save_to_csv(data, filename='gamerant_website_data.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"The scraped data has been saved to '{filename}'.")

# Main function to orchestrate the scraping
def scrape_gamerant_events():
    soup = get_soup(GAMERANT_WEBSITE_URL)
    if soup:
        events_data = scrape_main_page(soup)
        save_to_csv(events_data)

