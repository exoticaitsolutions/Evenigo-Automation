import time
import csv
import os
from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from SiteUtilsConfig.utils import *
from Integration_With_Bubble.upload_image_in_bubble import send_csv_data_to_bubble
from urls import NINTENDO_WEBSITE_URL
from SiteUtilsConfig.config import *
from webdriver import driver_confrigration


def extract_game_details(game_url):
    driver = driver_confrigration()  # Create a new driver instance
    driver.get(game_url)
    time.sleep(5)  # Allow time for the page to load

    try:
        # Extract description
        description = driver.find_element(
            By.XPATH, '//*[@id="main"]/section[2]/div/div/div[1]/div/div/div/p'
        ).text
        print(f"Description for {game_url} =====> {description}")
    except Exception as e:
        print(f"Could not retrieve description for {game_url}")
        description = ""

    driver.quit()
    return description


def convert_date_format(date_str):
    try:
        # Parse the date assuming it's in MM/DD/YY format
        date_obj = datetime.strptime(date_str, "%m/%d/%y")
        # Convert and return it in DD/MM/YYYY format
        return date_obj.strftime("%d/%m/%Y")
    except ValueError as e:
        print(f"Error parsing date '{date_str}': {e}")
        return "Invalid date format"


def scrape_nintendo_games():
    print("Start scrapping for nintendo website")
    # Set up Chrome options
    driver = driver_confrigration()
    driver.get(NINTENDO_WEBSITE_URL)

    os.makedirs(csv_folder_name, exist_ok=True)  # Create folder if it doesn't exist
    csv_file_path = os.path.join(csv_folder_name, nintendo_file_name)

    headers = [
        "Image URL",
        "Event Name",
        "Event Type",
        "Event Type (text)",
        "Event Description",
        "Calendar",
        "All Day",
        "Public/Private",
        "Reported Count",
        "Start Date",
        "End Date",
        "Url",
        "Created By",
    ]

    # Check if the CSV file exists
    file_exists = os.path.isfile(csv_file_path)

    try:
        driver.get(NINTENDO_WEBSITE_URL)

        # Allow some time for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.y83ib"))
        )

        game_containers = driver.find_elements(By.CSS_SELECTOR, "div.y83ib")

        with open(csv_file_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(headers)

            for game in game_containers:
                try:
                    # Extract image URL
                    image_div = game.find_element(By.CSS_SELECTOR, "div.Kx-Os.hCSeY")
                    img_tag = image_div.find_element(By.TAG_NAME, "img")
                    img_url = (
                        img_tag.get_attribute("src")
                        if img_tag
                        else "No image URL found"
                    )

                    # Extract title
                    title_tag = game.find_element(
                        By.CSS_SELECTOR, "h2.s954l.qIo1e._39p7O.bC4e6"
                    )
                    title = title_tag.text.strip() if title_tag else "No title found"

                    # Extract release date
                    release_date_tag = game.find_element(By.CSS_SELECTOR, "div.k9MOS")
                    release_date_text = (
                        release_date_tag.text.strip()
                        if release_date_tag
                        else "No release date found"
                    )
                    game_link = game.find_element(By.XPATH, ".//a").get_attribute(
                        "href"
                    )
                    description = extract_game_details(game_link)

                    def extract_date_if_releases(date_text):
                        if "Releases" in date_text:
                            date_str = date_text.split("Releases")[1].strip().strip(",")
                        else:
                            date_str = date_text.strip().strip(",")
                        return date_str

                    release_date = extract_date_if_releases(release_date_text)
                    formatted_date = convert_date_format(release_date)

                    def get_next_date(formatted_date_str):
                        try:
                            # Parse the date in DD/MM/YYYY format
                            date = datetime.strptime(formatted_date_str, "%d/%m/%Y")
                            next_date = date + timedelta(days=1)
                            # Return the next date in the same format
                            return next_date.strftime("%d/%m/%Y")
                        except ValueError as e:
                            print(f"Error parsing date '{formatted_date_str}': {e}")
                            return "Invalid date format"

                    End_date = get_next_date(formatted_date)

                    # Extract price
                    price_tag = game.find_element(By.CSS_SELECTOR, "span.W990N.SH2al")
                    price = price_tag.text.strip() if price_tag else "No price found"
                    row = [
                        img_url,  # Image URL
                        title,  # Event Name
                        "Launch",  # Event Type
                        "Launch",  # Event Type
                        description,  # Event Description (not available)
                        Nintendo_CALENDAR_NAME,  # Calendar (not available)
                        "No",  # All Day
                        "Public",  # Public/private (assuming public)
                        "0",  # Reported Count
                        formatted_date,  # Start Date
                        End_date,  # End Date
                        game_link,  # Website url
                        "evenigoofficial+5@gmail.com",
                    ]

                    # Write the data to the CSV file
                    writer.writerow(row)

                except Exception as e:
                    print(f"An error occurred while processing a game: {e}")

    finally:
        driver.quit()
    print("Scraping completed for nintendo website")
    print(f"Data has been written to {csv_file_path}")
    print()
    send_csv_data_to_bubble(CalendarEnum.NINTENDO.value, csv_file_path)


# Run the scraper
if __name__ == "__main__":
    scrape_nintendo_games()
