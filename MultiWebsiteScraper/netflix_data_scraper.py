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

from Integration_With_Bubble.upload_image_in_bubble import send_images_to_bubble_images_api
from urls import NETFLIX_WEBSITE_URL


def convert_date(date_str, year=None):
    month_map = {
        'Jan.': '1', 'Feb.': '2', 'Mar.': '3', 'Apr.': '4', 'May': '5',
        'Jun.': '6', 'Jul.': '7', 'Aug.': '8', 'Sept.': '9', 'Oct.': '10',
        'Nov.': '11', 'Dec.': '12'}
    
    month_str, day = date_str.split()
    month = month_map.get(month_str, '0')  
    if year is None:
        year = datetime.now().year % 100  
    
    formatted_date = f"{month}/{day}/{year:02}"
    return formatted_date

def scrape_netflix_content():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")

    driver = Driver(uc=True, headless=False)
    driver.get(NETFLIX_WEBSITE_URL)

    extracted_data = []

    try:
        heading_range = range(1, 5)
        paragraph_range = range(6, 10)
        paragraph2_range = range(14, 34)

        for number1, number3 in zip(heading_range, paragraph_range):
            xpath_heading = f'//*[@id="c-pageArticleSingle-new-on-netflix"]/div[1]/div[1]/div[2]/div/div/h3[{number1}]'
            xpath_paragraph = f'//*[@id="c-pageArticleSingle-new-on-netflix"]/div[1]/div[1]/div[2]/div/div/p[{number3}]'
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

                if ' (' in combined_text and ')' in combined_text:
                    date_pattern = r'\(([^)]+)\)'
                    match = re.search(date_pattern, combined_text)
                    name_part, start_date_part = combined_text.split(' (', 1)
                    name_part = name_part.strip()
                    if match:
                        date = match.group(1)
                        current_year = datetime.now().year % 100  
                        converted_date = convert_date(date, year=current_year)

                        def get_next_date(release_date_str):
                            try:
                                date = datetime.strptime(release_date_str, '%m/%d/%y')
                                next_date = date + timedelta(days=1)
                                return next_date.strftime('%m/%d/%y')
                            except ValueError as e:
                                print(f"Error parsing date '{release_date_str}': {e}")
                                return 'Invalid date format'

                        End_date = get_next_date(converted_date)

                        description = re.sub(date_pattern, '', combined_text).strip()
                    else:
                        print("No date found in the description.")
                    extracted_data.append({
                         "Image URL": '',
                         "Event Name": name_part,
                         "Event Type": "Sale",
                         "Event Description": description,
                         "Calendar": "Netflix",
                         "All Day": "No",
                         "Public/Private": "Public",
                         "Reported Count": 0,
                         "Start Date": converted_date,
                         "End Date": End_date,
                         "Url": NETFLIX_WEBSITE_URL,
                         "Created By":''
                    })
            except Exception as e:
                print(f"An error occurred for XPaths '{xpath_heading}' and '{xpath_paragraph}': {e}")

        for number in paragraph2_range:
            xpath = f'//*[@id="c-pageArticleSingle-new-on-netflix"]/div[1]/div[1]/div[2]/div/div/p[{number}]'
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                element = driver.find_element(By.XPATH, xpath)
                text = element.text
                
                lines = text.split('\n')
                date = lines[0].strip()
                current_year = datetime.now().year % 100  
                converted_date = convert_date(date, year=current_year)

                def get_next_date(release_date_str):
                    try:
                        date = datetime.strptime(release_date_str, '%m/%d/%y')
                        next_date = date + timedelta(days=1)
                        return next_date.strftime('%m/%d/%y')
                    except ValueError as e:
                        print(f"Error parsing date '{release_date_str}': {e}")
                        return 'Invalid date format'

                End_date = get_next_date(converted_date)
                events = "\n".join(line.strip() for line in lines[1:])
                
                extracted_data.append({
                    "Image URL": '',
                    "Event Name": events,
                    "Event Type": "Sale",
                    "Event Description": '',
                    "Calendar": "Netflix",
                    "All Day": "No",
                    "Public/Private": "Public",
                    "Reported Count": 0,
                    "Start Date": converted_date,
                    "End Date": End_date,
                    "Url": NETFLIX_WEBSITE_URL,
                    "Created By":''
                })
            except Exception as e:
                print(f"An error occurred for XPath '{xpath}': {e}")

        folder_path = 'csv_output'
        os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist
        csv_file_path = os.path.join(folder_path, 'netflix_data.csv')

        # Define CSV headers
        headers = [
            'Image URL', 'Event Name', 'Event Type', 'Event Description', 'Calendar', 'All Day',
            'Public/Private', 'Reported Count', 'Start Date', 'End Date', 'Url', 'Created By'
        ]

        # Write the data to the CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(extracted_data)

        print(f"Data has been written to {csv_file_path}")
        send_images_to_bubble_images_api(csv_file_path)

        # Optional: Add a delay
        time.sleep(2)

    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()
    

if __name__ == "__main__":
    scrape_netflix_content()