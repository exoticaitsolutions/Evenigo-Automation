import time
import csv
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from website_urls import NINTENDO_WEBSITE_URL

# Function to set up the WebDriver
def setup_driver():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    driver = Driver(uc=True, headless=False)
    return driver

# Function to wait for the page elements to load
def wait_for_page_load(driver):
    # Allow time for the page to load
    time.sleep(5)

    # Wait for the game containers to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.y83ib'))
    )

# Function to scrape data from a single game container
def scrape_game_data(game):
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

        return [title, release_date, price, img_url]
    
    except Exception as e:
        print(f"An error occurred while processing a game: {e}")
        return None

# Function to write data to CSV
def write_to_csv(data, csv_file_path):
    file_exists = os.path.isfile(csv_file_path)
    
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the header row only if the file does not exist
        if not file_exists:
            writer.writerow(['Title', 'Release Date', 'Price', 'Image URL'])
        
        for game_data in data:
            if game_data:
                writer.writerow(game_data)

# Main function to run the scraping process
def scrape_nintendo_games():
    driver = setup_driver()

    try:
        # Open the webpage
        driver.get(NINTENDO_WEBSITE_URL)
        
        wait_for_page_load(driver)

        # Find all game containers
        game_containers = driver.find_elements(By.CSS_SELECTOR, 'div.y83ib')

        # Collect the game data
        game_data = []
        for game in game_containers:
            data = scrape_game_data(game)
            if data:
                game_data.append(data)

        # Define the CSV file path
        csv_file_path = 'games_data.csv'

        # Write the collected data to the CSV file
        write_to_csv(game_data, csv_file_path)
        
    finally:
        # Quit the driver
        driver.quit()

    print(f"Data has been written to {csv_file_path}")

# Run the scraping process
if __name__ == "__main__":
    scrape_nintendo_games()
