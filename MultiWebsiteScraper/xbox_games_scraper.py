import os
from selenium.webdriver.common.by import By
from seleniumbase import Driver
from time import sleep
import csv
import re
from Integration_With_Bubble.upload_image_in_bubble import send_images_to_bubble_images_api
from urls import XBOX_GAMES_WEBSITE_URL
from SiteUtilsConfig.utils import *
from webdriver import driver_confrigration
from SiteUtilsConfig.config import *

def xbox_website_data_scraping():
    print("Scraping start for xbox website")
    driver = driver_confrigration()
    driver.get(XBOX_GAMES_WEBSITE_URL)
    sleep(25)

    cards = []
    try:
        driver.find_element(By.XPATH, '//*[@id = "unique-id-for-paglist-generated-select-menu-trigger"]').click()
        driver.find_element(By.XPATH, '//li[@id= "unique-id-for-paglist-generated-select-menu-3"]').click()
        sleep(5)
        cards = driver.find_elements(By.XPATH, '//a[@class = "gameDivLink"]')
    except Exception as e:
        # print(f"Error occurred while fetching the cards: {e}")
        sleep(5)
        cards = driver.find_elements(By.XPATH, '//a[@class = "gameDivLink"]')

    if cards:
        data = []
        price_pattern = re.compile(r'\$\d+\.\d{2}')

        for card in cards:
            # Extract the link and description
            link = card.get_attribute('href')
            desc = card.text
            match = price_pattern.search(desc)
            price = match.group(0) if match else 'N/A'

            # Find the image relative to the current card
            try:
                img = card.find_element(By.XPATH, './/*[@class = "containerIMG"]//img')
                img_link = img.get_attribute('src')
            except Exception as img_err:
                print(f"Image not found for card: {desc}, error: {img_err}")
                img_link = 'N/A'

            # Append data to the list
            data.append([img_link, desc, 'Sale', '', 'Xbox Calendar', 'No', 'Public', '0', '', '', link, 'evenigoofficial+1267@gmail.com'])

        # Write data to CSV
        os.makedirs(csv_folder_name, exist_ok=True)  # Create folder if it doesn't exist
        csv_file_path = os.path.join(csv_folder_name, xbox_file_name)
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Image URL', 'Event Name', 'Event Type', 'Event Description', 'Calendar', 'All Day', "Public/Private", 'Reported Count', 'Start Date', 'End Date', 'Url', "Created By"])  # Header row
            writer.writerows(data)

        print("Content saved to 'xbox_games_data.csv'.")
    else:
        print("Cards weren't found even in exception")

    # Close the WebDriver
    driver.quit()
    print("Scraping completed for xbox website")
    print(f"Data saved to {csv_file_path}.")
    print()

    # Send the data via the Bubble API
    send_images_to_bubble_images_api(CalendarEnum.Xbox_Calendar.value, csv_file_path)

# Run the scraper
if __name__ == "__main__":
    xbox_website_data_scraping()
