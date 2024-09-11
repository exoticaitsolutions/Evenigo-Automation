import time
import csv
import os
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

    # Define the URL
    url = NINTENDO_WEBSITE_URL

    # Define the CSV file path
    csv_file_path = 'nintendo_data.csv'

    headers = [
        'Event Name', 'All Day', 'Calendar', 'Created By', 'End Date',
        'Event Type', 'Public/private', 'Start Date', 'URL'
    ]

    # Check if the CSV file exists
    file_exists = os.path.isfile(csv_file_path)

    try:
        driver.get(url)
        
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
                    release_date = release_date_tag.text.strip() if release_date_tag else 'No release date found'

                    # Extract price
                    price_tag = game.find_element(By.CSS_SELECTOR, 'span.W990N.SH2al')
                    price = price_tag.text.strip() if price_tag else 'No price found'

                    # Create a row of data matching the headers
                    row = [
                        title,          # Event Name
                        'Yes',          # All Day (assuming all events are all day)
                        '',             # Calendar (not available in the current data)
                        '',             # Created By (not available in the current data)
                        '',             # End Date (not available in the current data)
                        'Event',        # Event Type (assuming all items are events)
                        'Public',       # Public/private (assuming all items are public)
                        release_date,   # Start Date (mapped to release date)
                        img_url         # URL (mapped to image URL)
                    ]

                    # Write the data to the CSV file
                    writer.writerow(row)

                except Exception as e:
                    print(f"An error occurred while processing a game: {e}")

    finally:
        driver.quit()

    print(f"Data has been written to {csv_file_path}")
        