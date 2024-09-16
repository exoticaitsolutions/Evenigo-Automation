import os
from SiteUtilsConfig.config import FILE_NAME, FILE_PATH
from selenium.webdriver.common.by import By
from time import sleep
import csv, re
from urls import XBOX_GAMES_WEBSITE_URL
from web_driver import initialize_driver

def xbox_website_data_scraping():
        driver = initialize_driver()
        driver.get(XBOX_GAMES_WEBSITE_URL)
        sleep(25)
        cards = 0
        try:
            driver.find_element(By.XPATH, '//*[@id = "unique-id-for-paglist-generated-select-menu-trigger"]').click()
            driver.find_element(By.XPATH, '//li[@id= "unique-id-for-paglist-generated-select-menu-3"]').click()
            sleep(5)
            cards = driver.find_elements(By.XPATH, '//a[@class = "gameDivLink"]')
        except:
            sleep(5)
            cards = driver.find_elements(By.XPATH, '//a[@class = "gameDivLink"]')

        if cards:
            i = 1
            data = []
            price_pattern = re.compile(r'\$\d+\.\d{2}')
            for card in cards:
                link = card.get_attribute('href')
                desc = card.text
                match = price_pattern.search(desc)
                price = match.group(0) if match else 'N/A'
                img = card.find_element(By.XPATH, '//*[@class = "containerIMG"]//img')
                img_link = img.get_attribute('src')
                # data.append([link, desc, price,img_link])
                data.append([desc, 'Event', '', 'Xbox Calander', 'No', 'Public', '0', '', '', link, img_link, ''])
                i+=1
            folder_path = 'csv_output'
            csv_file_path = os.path.join(FILE_PATH, FILE_NAME.get("XBOX_GAMES_WEBSITE"))
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # writer.writerow(['Link', 'Description', 'Price','Image link'])  # Header row
                writer.writerow(['Event Name', 'Event Type', 'Event Description', 'Calendar', 'All Day',
        'Public/private', "Reported Count", 'Start Date', 'End Date', 'URL', 'Image URL', 'Created By'])  # Header row
                writer.writerows(data)

            print("Content saved to 'xbox_games_data.csv'.")
        else:
            print("Cards weren't found even in exception")

        # Close the WebDriver
        driver.quit()
