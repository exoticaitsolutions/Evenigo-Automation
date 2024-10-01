import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from seleniumbase import Driver
from time import sleep
from datetime import datetime, timedelta
import re, csv
from SiteUtilsConfig.utils import *
from webdriver import driver_confrigration
from SiteUtilsConfig.config import *
from Integration_With_Bubble.upload_image_in_bubble import send_csv_data_to_bubble
from urls import PRIME_WEBSITE_URL

def parse_date(date_str):
    day = re.search(r"\d{1,2}", date_str)
    if day:
        day = int(day.group())
        date_str = f"2024-09-{day:02d}"
        return datetime.strptime(date_str, "%Y-%m-%d")
    return None


def scrape_prime_content():
    print("Scraping start for prime website")
    driver = driver_confrigration()
    driver.get(PRIME_WEBSITE_URL)
    sleep(5)
    data = []  
    img_elements = []
    try:
        main_heading_xpath = f'//*[@id="c-pageArticleSingle-new-on-amazon-prime-video"]/div[1]/div[1]/div[1]/h1'
        main_heading_element = driver.find_element(By.XPATH, main_heading_xpath)
        headings = []
        driver.execute_script(f"window.scrollBy(0, document.body.scrollHeight * 0.6);")
        sleep(2)
        img_elements = driver.find_elements(By.XPATH, '//*[@class = "c-cmsImage"]//img')
        for img_ele in img_elements[10:21]:
            img = img_ele.get_attribute("src")
        for i in range(1, 4):
            heading_xpath = f'//*[@id="c-pageArticleSingle-new-on-amazon-prime-video"]/div[1]/div[1]/div[2]/div/div/h3[{i}]/strong'
            heading_element = driver.find_element(By.XPATH, heading_xpath)
            full_text = heading_element.text

            if "(" in full_text and ")" in full_text:
                heading, start_date = full_text.split("(")
                date_str = start_date.replace(")", "").strip()
                start_date = parse_date(date_str)
                end_date = start_date + timedelta(days=1) if start_date else "N/A"
            else:
                heading = full_text
                start_date = "N/A"
                end_date = "N/A"
            headings.append((heading, start_date, end_date))

        first_imgs = img_elements[10:14]
        j = 1
        for i in range(6, 10):
            description_element = driver.find_element(
                By.XPATH,
                f'//*[@id="c-pageArticleSingle-new-on-amazon-prime-video"]/div[1]/div[1]/div[2]/div/div/p[{i}]',
            )
            description = description_element.text
            if i - 6 < len(headings):
                heading, start_date, end_date = headings[i - 6]
                event_name = main_heading_element.text
                description_without_date = heading + description
                img = first_imgs[j].get_attribute("src")
                start_date = (
                    start_date.strftime("%Y-%m-%d") if start_date != "N/A" else "N/A"
                )
                end_date = end_date.strftime("%Y-%m-%d") if end_date != "N/A" else "N/A"
                data.append(
                    [
                        "",
                        heading,
                        "Launch",
                        "Launch",
                        description,
                        Prime_Video_CALENDAR_NAME,
                        "No",
                        "Public",
                        "0",
                        start_date,
                        end_date,
                        PRIME_WEBSITE_URL,
                        "evenigoofficial+1269@gmail.com",
                    ]
                )
                j += 1

        sec_imgs = img_elements[4:21]
        j = 1
        for i in range(11, 28):
            second_ele = driver.find_element(
                By.XPATH,
                f"//*[@id='c-pageArticleSingle-new-on-amazon-prime-video']/div[1]/div[1]/div[2]/div/div/p[{i}]",
            )
            text_content = second_ele.text
            split_text = text_content.split("\n", 1)

         
            start_date_str = split_text[0].strip() if len(split_text) > 0 else "No date"


            description = (
                split_text[1].strip()
                if len(split_text) > 1
                else "No description available"
            )
            
            print("print the  description====>>>", description)
            event_names = description.splitlines()

            start_date = parse_date(start_date_str)
            if start_date:
                end_date = start_date + timedelta(days=1)
                start_date = start_date.strftime("%Y-%m-%d")
                print("print start date ====>",start_date)
                end_date = end_date.strftime("%Y-%m-%d")
                print("end date print =====>>",end_date)
            else:
                start_date = "N/A"
                end_date = "N/A"

            for event in event_names:
                print("event name print ====>",event)
                data.append(
                    [
                        "",
                        event,
                        "Launch",
                        "Launch",
                        "",
                        Prime_Video_CALENDAR_NAME,
                        "No",
                        "Public",
                        "0",
                        start_date,
                        end_date,
                        PRIME_WEBSITE_URL,
                        "evenigoofficial+1269@gmail.com",
                    ]
                )
            j += 1

    except Exception as e:
        print(f"An error occurred: {e}")

    os.makedirs(csv_folder_name, exist_ok=True)  
    csv_file_path = os.path.join(csv_folder_name, prime_file_name)

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
    driver.quit()
    print("Scraping completed for prime website")
    print(f"Data has been written to {csv_file_path}")
    print()
    send_csv_data_to_bubble(CalendarEnum.PRIME_VIDEO.value, csv_file_path)


if __name__ == "__main__":
    scrape_prime_content()
