import time
import csv
import os
from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver

from website_urls import NINTENDO_WEBSITE_URL


def scrape_nintendo_games():
    # Set up Chrome options
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")

    # Initialize the WebDriver
    driver = Driver(uc=True, headless=False)

    # Define the folder and CSV file path
    folder_path = 'csv_output'
    os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist
    csv_file_path = os.path.join(folder_path, 'nintendo_data.csv')

    headers = [
        'Event Name', 'Event Type', 'Event Description', 'Calendar', 'All Day',
        'Public/private', "Reported Count", 'Start Date', 'End Date', 'Created By', 'URL', 'Image URL'
    ]

    # Check if the CSV file exists
    file_exists = os.path.isfile(csv_file_path)

    try:
        driver.get(NINTENDO_WEBSITE_URL)
        
        # Allow some time for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.y83ib'))
        )

        game_containers = driver.find_elements(By.CSS_SELECTOR, 'div.y83ib')

        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            if not file_exists:
                writer.writerow(headers)

            for game in game_containers:
                try:
                    # Extract image URL
                    image_div = game.find_element(By.CSS_SELECTOR, 'div.Kx-Os.hCSeY')
                    img_tag = image_div.find_element(By.TAG_NAME, 'img')
                    img_url = img_tag.get_attribute('src') if img_tag else 'No image URL found'

                    # Extract title
                    title_tag = game.find_element(By.CSS_SELECTOR, 'h2.s954l.qIo1e._39p7O.bC4e6')
                    title = title_tag.text.strip() if title_tag else 'No title found'

                    # Extract release date
                    release_date_tag = game.find_element(By.CSS_SELECTOR, 'div.k9MOS')
                    release_date_text = release_date_tag.text.strip() if release_date_tag else 'No release date found'

                    def extract_date_if_releases(date_text):
                        if 'Releases' in date_text:
                            date_str = date_text.split('Releases')[1].strip().strip(',')
                            return date_str
                        else:
                            return date_text.strip().strip(',')

                    release_date = extract_date_if_releases(release_date_text)
                    
                    def get_next_date(release_date_str):
                        try:
                            date = datetime.strptime(release_date_str, '%m/%d/%y')
                            next_date = date + timedelta(days=1)
                            return next_date.strftime('%m/%d/%y')
                        except ValueError as e:
                            print(f"Error parsing date '{release_date_str}': {e}")
                            return 'Invalid date format'

                    End_date = get_next_date(release_date)

                    # Extract price
                    price_tag = game.find_element(By.CSS_SELECTOR, 'span.W990N.SH2al')
                    price = price_tag.text.strip() if price_tag else 'No price found'

                    row = [
                        title,              # Event Name
                        'Sale',             # Event Type
                        '',                 # Event Description (not available)
                        'sephora Calendar', # Calendar (not available)
                        'No',               # All Day
                        'Public',           # Public/private (assuming public)
                        '0',                # Reported Count
                        release_date,       # Start Date
                        End_date,           # End Date
                        NINTENDO_WEBSITE_URL,  # Created By
                        img_url             # Image URL
                    ]

                    # Write the data to the CSV file
                    writer.writerow(row)

                except Exception as e:
                    print(f"An error occurred while processing a game: {e}")

    finally:
        driver.quit()

    print(f"Data has been written to {csv_file_path}")


# Run the scraper
if __name__ == "__main__":
    scrape_nintendo_games()
