import re
import os
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
from webdriver_manager.chrome import ChromeDriverManager


# Function to handle the scraping process
def scrape_data(retry_count=0):
    start_time = time.time()
    try:
        # Set up the Chrome WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--start-maximized")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        driver.maximize_window()

        # Navigate to the desired webpage
        url = "https://www.sephora.com/beauty/beauty-offers"
        driver.get(url)
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
                    scrape_data()
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
                        event_name = card.text.split('\n')[0]

                        # event_name = text_lines[0] if len(text_lines) > 0 else "N/A"
                        # event_description = (
                        #     text_lines[1] if len(text_lines) > 1 else "N/A"
                        # )
                        event_description = card.text.split('\n')[1]
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

                        if (
                            image_url is None
                            or image_url
                            == "https://www.sephora.com/contentimages/happening/experienceimage.jpg"
                        ):
                            retry_count += 1
                            if retry_count < 2:
                                print(
                                    f"Image URL '{image_url}' is invalid. Retrying... Attempt {retry_count}/2"
                                )
                                driver.quit()
                                scrape_data(retry_count)
                                return
                            else:
                                image_url = image_url

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
                            }
                        )

                        scraped_items.add(event_name)
                    break

                except StaleElementReferenceException:
                    print("Stale element reference encountered. Re-fetching the list.")
                    driver.get(url)
                    time.sleep(3)
                    driver.execute_script(
                        "window.scrollBy(0, window.innerHeight * 0.9);"
                    )
                    time.sleep(3)
                print(len(all_feeds))
            except (WebDriverException, Exception) as e:
                print(f"An unexpected error occurred: {e}")
                driver.quit()
                scrape_data(retry_count)
                return

        df = pd.DataFrame(data)

        if df.empty:
            print("No data to save. Retrying...")
            driver.quit()
            scrape_data(retry_count)
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
                paragraphs.append(row["Paragraph 2"])
            if pd.notna(row["Paragraph 3"]):
                paragraphs.append(row["Paragraph 3"])
            if pd.notna(row["Paragraph 5"]):
                paragraphs.append("\n" + row["Paragraph 5"])
            return row["Event Description"] + "\n" + "\n".join(paragraphs)

        df["Event Description"] = df.apply(concatenate_paragraphs, axis=1)
        df = df.drop(columns=["Paragraph 2", "Paragraph 3", "Paragraph 5"])

        # Remove special characters from all columns except 'Image URL'
        special_characters = r"[¶•§§\^\*†‡‡â€¡â€¡]"
        for col in df.columns:
            if col != "Image URL":
                df[col] = df[col].apply(
                    lambda x: (
                        re.sub(special_characters, "", str(x)) if pd.notna(x) else x
                    )
                )

        # Save the DataFrame to a CSV file
        csv_file = "sephora_beauty_offers.csv"
        df.to_csv(csv_file, index=False)

        print(f"CSV file created: {csv_file}")
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total execution time: {total_time:.2f} seconds")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        driver.quit()
