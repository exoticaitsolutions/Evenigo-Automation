
import time
import time
import csv, re
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from website_urls import NETFLIX_WEBSITE_URL

def scrape_netflix_content():
    # Set up Chrome options
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")

    # Initialize the WebDriver
    driver = Driver(uc=True, headless=False)

    driver.get(NETFLIX_WEBSITE_URL)

    extracted_data = []

    try:
        heading_range = range(1, 4)  
        paragraph_range = range(6, 10) 
        paragraph2_range = range(14, 34) 

        # Extract data from <h3> elements
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
                        description = re.sub(date_pattern, '', combined_text).strip()
                        print(f"Date: {date}")
                        print(f"Description: {description}")
                    else:
                        print("No date found in the description.")
                    extracted_data.append({
                        'Event Name': name_part,
                        'All Day': 'Yes',
                        'Calendar': '',
                        'Created By': '',
                        'End Date': '',
                        'Event Type': 'Event',
                        'Public/private': 'Public',
                        'Start Date': date,
                        'URL': '',
                        'Short Description': description
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
                events = "\n".join(line.strip() for line in lines[1:])  
                
                extracted_data.append({
                    'Event Name': events,
                    'All Day': 'No',
                    'Calendar': '',
                    'Created By': '',
                    'End Date': '',
                    'Event Type': 'Event',
                    'Public/private': 'Public',
                    'Start Date': date,
                    'URL': '',
                    'Short Description': ''
                })

            except Exception as e:
                print(f"An error occurred for XPath '{xpath}': {e}")

        csv_file_path = 'extracted_events.csv'

        # Define CSV headers
        headers = [
            'Event Name', 'All Day', 'Calendar', 'Created By', 'End Date',
            'Event Type', 'Public/private', 'Start Date', 'URL', 'Short Description'
        ]

        # Write the data to the CSV file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(extracted_data)

        print(f"Data has been written to {csv_file_path}")

        # Optional: Add a delay
        time.sleep(2)

    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()