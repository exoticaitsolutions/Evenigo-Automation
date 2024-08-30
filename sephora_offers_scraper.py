import re
import time
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
from upload_image_in_bubble import send_images_to_bubble_images_api
from webdriver_manager.chrome import ChromeDriverManager
from sephora_urls import *
from seleniumbase import Driver

from selenium.webdriver.support import expected_conditions as EC

def scrape_sephora_website_offers(retry_count=0):
    """
    Scrapes promotional offers from the Sephora website and saves the data to a CSV file.

    Parameters:
    retry_count (int): The number of times to retry the scraping process in case of failure. Defaults to 0.

    This function performs the following tasks:
    1. Initializes a Selenium WebDriver instance with specified options.
    2. Navigates to the Sephora website and handles potential popups.
    3. Scrolls through the page to collect information about promotional offers.
    4. Extracts data including event names, descriptions, images, and dates.
    5. Cleans and processes the extracted data.
    6. Saves the processed data to a CSV file.
    7. Uploads images related to the offers to Bubble.

    It handles various exceptions including timeouts and stale element references, and retries the scraping process if necessary.
    """
    start_time = time.time()
    try:
        # Set up the Chrome WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--start-maximized")
        driver = Driver(uc=True, headless=False)

        driver.maximize_window()

        # Navigate to the desired webpage
        driver.get(SEPHORA_WEBSITE_URL)
        time.sleep(7)

        data = []
        img_urls = []
        scraped_items = set()

        def close_popup(xpath):
            try:
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                driver.find_element(By.XPATH, xpath).click()
                print(f"Popup with XPath '{xpath}' closed.")
            except (NoSuchElementException, TimeoutException):
                print(f"Popup with XPath '{xpath}' not found or not clickable.")

        close_popup('//*[@id="modal2Dialog"]/button')
        close_popup('//*[@id="modal1Dialog"]/button')

        start_date = ""
        count = 0
        main = driver.find_element(
            By.XPATH, '//*[@data-comp = "LayoutOpen StyledComponent BaseComponent "]'
        )

        while len(img_urls) < 7:
            try:
                driver.execute_script(
                    "window.scrollBy(0, document.body.scrollHeight * 0.1);"
                )
                time.sleep(5)
                all_feeds = main.find_elements(
                    By.XPATH, '//*[@class="css-1fxtpxe eanm77i0"]'
                )
                print("All the sections are:", len(all_feeds))
                if len(all_feeds) == 0:
                    print("No members found. Retrying...")
                    driver.quit()
                    scrape_sephora_website_offers()
                    return

                if count < 15:
                    if (count % 7) == 0:
                        driver.execute_script(
                            "window.scrollBy(0, -document.body.scrollHeight * 0.6);"
                        )
                    count += 1
                    continue

                close_popup('//*[@id="modal2Dialog"]/button')
                if not all_feeds:
                    print("No data found. Exiting.")
                    break

                try:
                    mem = all_feeds[0]
                    card_elements_today_offers = mem.find_elements(By.XPATH, '//li[@class="css-1jz9muy eanm77i0"]')
                    print("cards :", len(card_elements_today_offers))
                    if card_elements_today_offers:
                        for j in card_elements_today_offers:
                            link_element = j.find_element(By.TAG_NAME, 'a')
                            href_link = link_element.get_attribute('href')
                            print("---------------------------------------"*8)
                            print('card_elements_today_offers : ', j.text)
                            print('href link: ', href_link)
                            img_element = j.find_element(By.TAG_NAME, 'img')
                            img_src = img_element.get_attribute('src')
                            print('image src: ', img_src)
                            text_lines = j.text.split("\n")
                            event_name = j.text.split("\n")[0]
                            event_description = j.text.split("\n")[1]
                            # if event_description in scraped_items:
                            #     continue

                            paragraph_2 = text_lines[2] if len(text_lines) > 2 else ""
                            paragraph_3 = text_lines[3] if len(text_lines) > 3 else ""
                            paragraph_5 = text_lines[5] if len(text_lines) > 5 else ""

                            print(f"Event Name: {event_name}")
                            print(f"Event Description: {event_description}")
                            print(f"Paragraph 2: {paragraph_2}")
                            print(f"Paragraph 3: {paragraph_3}")
                            print(f"Paragraph 5: {paragraph_5}")
                            print("---------------------------------------"*8)
                            data.append(
                            {
                                "Image URL": img_src,
                                "Event Name": event_name,
                                "Event Type": "Sale",
                                "Event Description": event_description,
                                "Calendar": "sephora Calendar",
                                "All Day": "No",
                                "Public/Private": "Public",
                                "Reported Count": 0,
                                "Paragraph 2": paragraph_2,
                                "Paragraph 3": paragraph_3,
                                "Start Date": start_date,
                                "End Date": '',
                                "Paragraph 5": paragraph_5,
                                "Url": href_link,
                            }
                        )
                    card_elements = mem.find_elements(
                        By.XPATH, '//li[@class="css-6bi8ut eanm77i0"]'
                    )
                    print("Cards are", len(card_elements))
                    driver.execute_script(
                        "window.scrollBy(0, -document.body.scrollHeight * 0.5);"
                    )
                    time.sleep(5)

                    for card in card_elements:
                        heading = card.text
                        print()
                        print("Data:", heading)

                        text_lines = card.text.split("\n")
                        event_name = card.text.split("\n")[0]
                        event_description = card.text.split("\n")[1]
                        if event_description in scraped_items:
                            continue

                        paragraph_2 = text_lines[2] if len(text_lines) > 2 else ""
                        paragraph_3 = text_lines[3] if len(text_lines) > 3 else ""
                        paragraph_5 = text_lines[5] if len(text_lines) > 5 else ""

                        print(f"Event Name: {event_name}")
                        print(f"Event Description: {event_description}")
                        print(f"Paragraph 2: {paragraph_2}")
                        print(f"Paragraph 3: {paragraph_3}")
                        print(f"Paragraph 5: {paragraph_5}")

                        image_element = card.find_element(By.XPATH, ".//img")
                        image_url = image_element.get_attribute("src")
                        print("Image URL:", image_url)

                        end_date = ""
                        for line in text_lines:
                            if "Ends" in line:
                                end_date = line.split("Ends")[-1].strip()
                                break

                        if "Ends" in paragraph_2:
                            paragraph_2 = re.sub(r"Ends.*", "", paragraph_2).strip()

                        if "Ends" in paragraph_3:
                            paragraph_3 = re.sub(r"Ends.*", "", paragraph_3).strip()

                        data.append(
                            {
                                "Image URL": image_url,
                                "Event Name": event_name,
                                "Event Type": "Sale",
                                "Event Description": event_description,
                                "Calendar": "sephora Calendar",
                                "All Day": "No",
                                "Public/Private": "Public",
                                "Reported Count": 0,
                                "Paragraph 2": paragraph_2,
                                "Paragraph 3": paragraph_3,
                                "Start Date": start_date,
                                "End Date": end_date,
                                "Paragraph 5": paragraph_5,
                                "Url": "https://www.sephora.com/beauty/beauty-offers",
                            }
                        )

                        scraped_items.add(event_name)
                    break

                except StaleElementReferenceException:
                    print("Stale element reference encountered. Re-fetching the list.")
                    driver.get(SEPHORA_WEBSITE_URL)
                    time.sleep(3)
                    driver.execute_script(
                        "window.scrollBy(0, window.innerHeight * 0.9);"
                    )
                    time.sleep(3)
                print(len(all_feeds))
            except (WebDriverException, Exception) as e:
                print(f"An unexpected error occurred: {e}")
                driver.quit()
                scrape_sephora_website_offers(retry_count)
                return

        df = pd.DataFrame(data)

        if df.empty:
            print("No data to save. Retrying...")
            driver.quit()
            scrape_sephora_website_offers(retry_count)
            return

        # Add placeholder for End Date if missing
        def add_placeholder_end_date(row):
            if pd.isna(row["End Date"]) or row["End Date"].strip() == "":
                if pd.notna(row["Start Date"]):
                    start_date = pd.to_datetime(
                        row["Start Date"], errors="coerce"
                    )  # Convert to datetime, coerce errors to NaT
                else:
                    start_date = (
                        datetime.now()
                    )  # Use current date if Start Date is missing

                if pd.isna(start_date):
                    # If start_date is NaT, use the current date
                    start_date = datetime.now()

                end_date = start_date + timedelta(days=7)
                return end_date.strftime("%Y-%m-%d")
            return row["End Date"]

        df["End Date"] = df.apply(add_placeholder_end_date, axis=1)

        # Concatenate paragraphs into Event Description
        def concatenate_paragraphs(row):
            paragraphs = []
            if pd.notna(row["Paragraph 2"]):
                paragraphs.append("\n" + row["Paragraph 2"])
            if pd.notna(row["Paragraph 3"]):
                paragraphs.append("\n" + row["Paragraph 3"])
            if pd.notna(row["Paragraph 5"]):
                paragraphs.append("\n" + row["Paragraph 5"])

            return row["Event Description"] + "\n" + "\n".join(paragraphs)

        df["Event Description"] = df.apply(concatenate_paragraphs, axis=1)
        df = df.drop(columns=["Paragraph 2", "Paragraph 3", "Paragraph 5"])

        special_characters = r"[¶•§§\^\*†‡‡â€¡â€¡稚熔容痴熔®â€™â€™]"
        for col in df.columns:
            if col != "Image URL":
                df[col] = df[col].apply(
                    lambda x: (
                        re.sub(special_characters, "", str(x)) if pd.notna(x) else x
                    )
                )

        csv_file = "sephora_beauty_offers.csv"
        df.to_csv(csv_file, index=False)

        print(f"CSV file created: {csv_file}")
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Scraping completed. Data saved to 'sephora_beauty_offers.csv'.")
        print(f"Total execution time: {total_time:.2f} seconds")
        driver.quit()
        send_images_to_bubble_images_api(csv_file)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        driver.quit()
