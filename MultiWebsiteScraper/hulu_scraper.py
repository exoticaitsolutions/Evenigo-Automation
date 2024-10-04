import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import csv
import re
import time
from Integration_With_Bubble.upload_image_in_bubble import send_csv_data_to_bubble
from SiteUtilsConfig.utils import *
from SiteUtilsConfig.config import *
from urls import NEW_ON_HULU_WEBSITE_URL
from webdriver import driver_confrigration


# Convert date to DD-MM-YYYY format
def convert_date(date_str, year=None):
    month_map = {
        "Jan.": "1",
        "Feb.": "2",
        "Mar.": "3",
        "Apr.": "4",
        "May": "5",
        "Jun.": "6",
        "Jul.": "7",
        "Aug.": "8",
        "Sept.": "9",
        "Oct.": "10",
        "Nov.": "11",
        "Dec.": "12",
    }

    month_str, day = date_str.split()

    month = month_map.get(month_str, "0")
    if year is None:
        year = datetime.now().year

    # Format the date as DD-MM-YYYY
    formatted_date = f"{day.zfill(2)}-{month.zfill(2)}-{year}"
    return formatted_date


# Get the next date in DD-MM-YYYY format
def get_next_date(release_date_str):
    try:
        date = datetime.strptime(release_date_str, "%d-%m-%Y")
        next_date = date + timedelta(days=1)
        return next_date.strftime("%d-%m-%Y")  # Return in DD-MM-YYYY format
    except ValueError as e:
        print(f"Error parsing date '{release_date_str}': {e}")
        return "Invalid date format"


def scrape_hulu_content():
    print("Scraping start for hulu website")
    driver = driver_confrigration()
    driver.get(NEW_ON_HULU_WEBSITE_URL)

    data = []
    try:
        time.sleep(3)
        firsts = driver.find_elements(By.XPATH, "//h3//strong")

        titles1 = driver.find_elements(
            By.XPATH,
            '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/p',
        )
        image_element = driver.find_element(
            By.XPATH,
            '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/figure/div/div/picture/img',
        )
        # image_src = image_element.get_attribute("src")
        titles = titles1[6:9]


        for first, title in zip(firsts, titles):
            match = re.search(r"^(.*?)\s*\(([^)]+)\)$", first.text)
            heading = match.group(1).strip()
            date = match.group(2).strip()

            current_year = datetime.now().year
            converted_date = convert_date(date, year=current_year)
            end_date = get_next_date(converted_date)
            data.append(
                [
                    "",
                    heading,
                    "Launch",
                    "Launch",
                    title.text,
                    Hulu_CALENDAR_NAME,
                    "No",
                    "Public",
                    "0",
                    converted_date,
                    end_date,
                    NEW_ON_HULU_WEBSITE_URL,
                    "evenigoofficial+1262@gmail.com",
                ]
            )

        seconds1 = driver.find_elements(
            By.XPATH,
            '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/p/strong',
        )
        seconds = seconds1[10:34]
        titles = titles1[12:34]

        for second, title in zip(seconds, titles):
            sec = second.text
            tt = title.text
            date = tt.split(":")[0].strip()
            colon_index = tt.find(":")
            desc = tt[colon_index + 1 :].strip()
            event_names = desc.splitlines()
            for event in event_names:
                converted_date = convert_date(date, year=current_year)
                end_date = get_next_date(converted_date)
                data.append(
                    [
                        "",
                        event,
                        "Launch",
                        "Launch",
                        "",
                        Hulu_CALENDAR_NAME,
                        "No",
                        "Public",
                        "0",
                        converted_date,
                        end_date,
                        NEW_ON_HULU_WEBSITE_URL,
                        "evenigoofficial+1262@gmail.com",
                    ]
                )
    except Exception as e:
        print("--------- EXCEPTION ----------------------", str(e))

    finally:
        driver.quit()
        os.makedirs(csv_folder_name, exist_ok=True)
        csv_file_path = os.path.join(csv_folder_name, hulu_file_name)

        with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(
                [
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
            )
            csvwriter.writerows(data)
        print("Scraping completed for hulu website")
        print(f"Data has been written to {csv_file_path}")
        print()
        send_csv_data_to_bubble(CalendarEnum.Hulu_Calendar.value, csv_file_path)

# Run the scraper
if __name__ == "__main__":
    scrape_hulu_content()
