import time
import csv
import re
import os
from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from SiteUtilsConfig.utils import *
from SiteUtilsConfig.config import *
from Integration_With_Bubble.upload_image_in_bubble import send_csv_data_to_bubble
from urls import PRIME_WEBSITE_URL
from webdriver import driver_confrigration


def is_valid_date(date_str):
    """Check if the date string is in the correct format and valid."""
    try:
   
        date = datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False

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
        "October":"10",
        "Nov.": "11",
        "Dec.": "12",
    }

    date_str = date_str.strip("()")
    month_str, day = date_str.split()
    day = day.replace(".", "")  

    month = month_map.get(month_str, "0")

    if year is None:
        year = datetime.now().year  
    else:

        year = 2000 + int(year) if len(str(year)) == 2 else int(year)


    formatted_date = f"{int(day):02}-{int(month):02}-{year}"
    return formatted_date


def scrape_prime_content():
    print("Scraping start for prime website")
    driver = driver_confrigration()
    driver.get(PRIME_WEBSITE_URL)

    extracted_data = []

    try:
        heading_range = range(1, 5)
        paragraph_range = range(6, 10)
        paragraph2_range = range(12, 27) 


        for number1, number3 in zip(heading_range, paragraph_range):
            xpath_heading = f'//*[@id="c-pageArticleSingle-new-on-amazon-prime-video"]/div[1]/div[1]/div[2]/div/div/h3[{number1}]'
            xpath_paragraph = f'//*[@id="c-pageArticleSingle-new-on-amazon-prime-video"]/div[1]/div[1]/div[2]/div/div/p[{number3}]'
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath_heading))
                )
                heading_element = driver.find_element(By.XPATH, xpath_heading)
                heading_text = heading_element.text

                

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath_paragraph))
                )
                paragraph_element = driver.find_element(By.XPATH, xpath_paragraph)
                paragraph_text = paragraph_element.text

                
                
                
                combined_text = f"{heading_text} {paragraph_text}".strip()
               
                matches = re.split(r'(\(\w+\. \d{1,2}\))', combined_text)
                
                
                for i in range(0, len(matches), 3):  
                    title = matches[i].strip() if i < len(matches) else ""
                    date_part = matches[i+1].strip() if i+1 < len(matches) else ""
                    description = matches[i+2].strip().replace("[Trailer]", "") if i+2 < len(matches) else ""

                    # print(f"Title: {title}\nDescription: {description}\nDate: {date_part}\n")

                    if "(" in date_part and ")" in date_part:
                        converted_date = convert_date(date_part)
                        print(f"Converted Date: {converted_date}")
                
                    def get_next_date(release_date_str):
                 
                        if not is_valid_date(release_date_str):
                            print(f"Error: Invalid date '{release_date_str}'")
                            return "Invalid date format"
                    
                        date = datetime.strptime(release_date_str, "%d-%m-%Y")
                        next_date = date + timedelta(days=1)
                        
                     
                        return next_date.strftime("%d-%m-%Y")

                    End_date = get_next_date(converted_date)

                    extracted_data.append(
                        {
                            "Image URL": "",
                            "Event Name": title,
                            "Event Type": "Launch",
                            "Event Type (text)": "Launch",
                            "Event Description": description,
                            "Calendar": Prime_Video_CALENDAR_NAME,
                            "All Day": "No",
                            "Public/Private": "Public",
                            "Reported Count": 0,
                            "Start Date": converted_date,
                            "End Date": End_date,
                            "Url": PRIME_WEBSITE_URL,
                            "Created By": "evenigoofficial+1269@gmail.com",
                        }
                    )
            except Exception as e:
                print(
                    f"An error occurred for XPaths '{xpath_heading}' and '{xpath_paragraph}': {e}"
                )

        for number in paragraph2_range:
            xpath = f'//*[@id="c-pageArticleSingle-new-on-amazon-prime-video"]/div[1]/div[1]/div[2]/div/div/p[{number}]'
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                element = driver.find_element(By.XPATH, xpath)
                text = element.text

                lines = text.split("\n")
                date = lines[0].strip()
                current_year = datetime.now().year % 100
                converted_date = convert_date(date, year=current_year)

                def get_next_date(release_date_str):
                    try:
                   
                        date = datetime.strptime(release_date_str, "%d-%m-%Y")
                        next_date = date + timedelta(days=1)
                    
                        return next_date.strftime("%d-%m-%Y")
                    except ValueError as e:
                        print(f"Error parsing date '{release_date_str}': {e}")
                        return "Invalid date format"

                End_date = get_next_date(converted_date)
                events = "\n".join(line.strip() for line in lines[1:])
                event_names = events.splitlines()
                for event in event_names:
                    extracted_data.append(
                        {
                            "Image URL": "",
                            "Event Name": event,
                            "Event Type": "Launch",
                            "Event Type (text)": "Launch",
                            "Event Description": "",
                            "Calendar": Prime_Video_CALENDAR_NAME,
                            "All Day": "No",
                            "Public/Private": "Public",
                            "Reported Count": 0,
                            "Start Date": converted_date,
                            "End Date": End_date,
                            "Url": PRIME_WEBSITE_URL,
                            "Created By": "evenigoofficial+1269@gmail.com",
                        }
                    )
            except Exception as e:
                print(f"An error occurred for XPath '{xpath}': {e}")

        os.makedirs(csv_folder_name, exist_ok=True) 
        csv_file_path = os.path.join(csv_folder_name, prime_file_name)

      
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


        with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(extracted_data)
        print("Scraping completed for prime website")
        print(f"Data has been written to {csv_file_path}")
        print()
        driver.quit()
        send_csv_data_to_bubble(CalendarEnum.PRIME_VIDEO.value, csv_file_path)


        

  
        time.sleep(2)

    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_prime_content()