from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import csv
import re
import time

from website_urls import NEW_ON_HULU_WEBSITE_URL

def parse_date(date_str):
    day = re.search(r'\d{1,2}', date_str)
    if day:
        day = int(day.group())
        date_str = f'2024-09-{day:02d}' 
        return datetime.strptime(date_str, '%Y-%m-%d')
    return None

def format_description(desc):
    date_pattern = r'(Sept\.\s\d{1,2})'
    match = re.search(date_pattern, desc)
    if match:
        date_str = match.group(0)
        return desc.replace(date_str, '').strip()
    return desc

def scrape_hulu_content():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get(NEW_ON_HULU_WEBSITE_URL)

    data = []
    heading = driver.find_element(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/h2[1]/strong').text

    try:
        time.sleep(3)

        firsts = driver.find_elements(By.XPATH, '//h3//strong')
        titles1 = driver.find_elements(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/p')
        image_element = driver.find_element(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/figure/div/div/picture/img')
        image_src = image_element.get_attribute('src')
        if len(firsts) >= 5 and len(titles1) >= 10:
            titles = titles1[5:10]
            for first, title in zip(firsts, titles):
                data.append([heading, first.text + ": " + title.text])
        
        if len(titles1) >= 38:
            seconds1 = driver.find_elements(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-hulu"]/div[1]/div[1]/div[2]/div/div/p')
            seconds = seconds1[13:38]
            titles = titles1[12:38]
            i = 13
            for second in seconds:
                d = []
                if i < len(titles):
                    title = titles[i - 13].text 
                    d.append(title)
                data.append([heading, second.text + ": " + " ".join(d)])
                i += 1

        processed_data = []
        for heading, description in data:
            dates = re.findall(r'Sept\.\s\d{1,2}', description)
            if dates:
                for date_str in dates:
                    start_date = parse_date(date_str)
                    if start_date:
                        end_date = start_date + timedelta(days=1)
                        description_without_date = format_description(description)
                        processed_data.append([
                            image_src,
                            heading,
                            description_without_date,
                            'Calendar',
                            'All Day',
                            'Public',
                            '0',
                            start_date.strftime('%Y-%m-%d'),
                            end_date.strftime('%Y-%m-%d')
                        ])
                        print(f"Processed: {heading} | {start_date} | {end_date} | {description_without_date[:100]}...") 
                    else:
                        print(f"Failed to parse date: {date_str}")

        with open('hulu_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Image URL','Event Name', 'Event Description','Calendar','All Day','Public/Private','Reported Count', 'Start_Date', 'End_Date'])
            csvwriter.writerows(processed_data)

    except Exception as e:
        print("--------- EXCEPTION ----------------------", str(e))

    finally:
        driver.quit()
