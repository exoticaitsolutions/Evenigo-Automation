import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import csv
import re
import time
from urls import NEW_ON_HULU_WEBSITE_URL


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

def get_next_date(release_date_str):
    try:
        date = datetime.strptime(release_date_str, '%m/%d/%y')
        next_date = date + timedelta(days=1)
        return next_date.strftime('%m/%d/%y')
    except ValueError as e:
        print(f"Error parsing date '{release_date_str}': {e}")
        return 'Invalid date format'

def scrape_hulu_content():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get(NEW_ON_HULU_WEBSITE_URL)


    data = []
    try:
        time.sleep(3)
        firsts = driver.find_elements(By.XPATH, '//h3//strong')
        heading1 = driver.find_element(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/h2[1]/strong').text
        print("heading1 : ", heading1)
        description = driver.find_element(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/figure/figcaption/span[1]/p').text
        titles1 = driver.find_elements(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/p')
        image_element = driver.find_element(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/figure/div/div/picture/img')
        image_src = image_element.get_attribute('src')
        titles = titles1[5:10]
        data.append([image_src, heading1, description, 'hulu Calendar', 'No', 'Public', ' 0', '', '', NEW_ON_HULU_WEBSITE_URL, '', 'Event'])
        for first, title in zip(firsts, titles):
            match = re.search(r'^(.*?)\s*\(([^)]+)\)$', first.text)
            heading = match.group(1).strip()
            date = match.group(2).strip()
            current_year = datetime.now().year % 100  
            converted_date = convert_date(date, year=current_year)
            End_date = get_next_date(converted_date)
            data.append(['', heading, title.text, 'hulu Calendar', 'No', 'Public', ' 0', converted_date, End_date, NEW_ON_HULU_WEBSITE_URL, '', 'Event'])
        
        seconds1 = driver.find_elements(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/p/strong')
        seconds = seconds1[10:35]
        titles = titles1[13:38]
        for second, title in zip(seconds, titles):
            sec = second.text
            tt = title.text
            date = sec.rstrip(':')
            colon_index = tt.find(':')
            desc = tt[colon_index + 1:].strip()
            current_year = datetime.now().year % 100 
            converted_date = convert_date(date, year=current_year)
            End_date = get_next_date(converted_date)
            data.append(['', desc, '', 'hulu Calendar', 'No', 'Public', '0', converted_date, End_date, NEW_ON_HULU_WEBSITE_URL, '', 'Event'])

    except Exception as e:
        print("--------- EXCEPTION ----------------------", str(e))

    finally:
        driver.quit()
        folder_path = 'csv_output'
        os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist
        csv_file_path = os.path.join(folder_path, 'new_on_hulu.csv')
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Image URL','Event Name', 'Event Description', 'Calendar', 'All Day', 'Public/Private', 'Reported Count', 'Start_Date', 'End_Date', 'URL', 'Created By', 'Event Type'])
            csvwriter.writerows(data)
        print(f"Data has been written to {csv_file_path}")

# Run the scraper
if __name__ == "__main__":
    scrape_hulu_content()