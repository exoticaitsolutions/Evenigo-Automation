import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from seleniumbase import Driver
from time import sleep
from datetime import datetime, timedelta
import re, csv

from Integration_With_Bubble.upload_image_in_bubble import send_images_to_bubble_images_api
# from urls import PRIME_WEBSITE_URL

PRIME_WEBSITE_URL   = 'https://www.tvguide.com/news/new-on-amazon-prime-video/'
def parse_date(date_str):
    day = re.search(r'\d{1,2}', date_str)
    if day:
        day = int(day.group())
        date_str = f'2024-09-{day:02d}' 
        return datetime.strptime(date_str, '%Y-%m-%d')
    return None

def scrape_prime_content():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    driver = Driver(uc=True, headless=False)
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
            img = img_ele.get_attribute('src')
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
            description_element = driver.find_element(By.XPATH,f'//*[@id="c-pageArticleSingle-new-on-amazon-prime-video"]/div[1]/div[1]/div[2]/div/div/p[{i}]')
            description = description_element.text
            if i - 6 < len(headings):
                heading, start_date, end_date = headings[i - 6]
                event_name = main_heading_element.text
                description_without_date = heading + description
                img = first_imgs[j].get_attribute('src')
                start_date = start_date.strftime('%Y-%m-%d') if start_date != "N/A" else "N/A"
                end_date = end_date.strftime('%Y-%m-%d') if end_date != "N/A" else "N/A"
                data.append([
                    img,
                    heading,
                    'Sale',
                    description,
                    'Prime Video',
                    'No',
                    'Public',
                    '0',
                    start_date,
                    end_date,
                    PRIME_WEBSITE_URL,
                    '',
                ])
                j += 1

        sec_imgs = img_elements[4:21]
        j = 1
        for i in range(11, 27):
            second_ele = driver.find_element(By.XPATH, f"//*[@id='c-pageArticleSingle-new-on-amazon-prime-video']/div[1]/div[1]/div[2]/div/div/p[{i}]")
            text_content = second_ele.text
            split_text = text_content.split('\n', 1)

            start_date_str = split_text[0].strip()
            description = split_text[1].strip() if len(split_text) > 1 else "No description available"

            start_date = parse_date(start_date_str)
            if start_date:
                end_date = start_date + timedelta(days=1)
                start_date = start_date.strftime('%Y-%m-%d')
                end_date = end_date.strftime('%Y-%m-%d')
            else:
                start_date = "N/A"
                end_date = "N/A"

            img = sec_imgs[j].get_attribute('src')
            data.append( [
                '',
                description,
                'Sale',
                '',
                'Prime Video',
                'No',
                'Public',
                '0',
                start_date,
                end_date,
                PRIME_WEBSITE_URL,
                ''
            ])
            j += 1

    except Exception as e:
        print(f"An error occurred: {e}")
    folder_path = 'csv_output'
    os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist
    csv_file_path = os.path.join(folder_path, 'Amazon_prime_site.csv')

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        # csvwriter.writerow(['Event Name', 'Event Type', 'Event Description', 'Calendar', 'All Day','Public/private', "Reported Count", 'Start Date', 'End Date', 'Created By', 'Url', 'Image URL'])
        csvwriter.writerow(['Image URL', 'Event Name', 'Event Type', 'Event Description', 'Calendar','All Day', "Public/Private", 'Reported Count', 'Start Date', 'End Date', 'Url', "Created By"])

        csvwriter.writerows(data)
    driver.quit()
    print(f"Data has been written to {csv_file_path}")
    send_images_to_bubble_images_api(csv_file_path)

if __name__ == "__main__":
    scrape_prime_content()