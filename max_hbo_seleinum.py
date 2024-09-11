from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from seleniumbase import Driver
from time import sleep
import csv
from website_urls import NEW_ON_MAX_HBO_WEBSITE_URL

data = []
events_name = []
description_data = []
start_date_data = []

def xbox_website_data_scraping():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    driver = Driver(uc=True, headless=False)
    driver.get(NEW_ON_MAX_HBO_WEBSITE_URL)
    sleep(5)

    # Scroll down the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.6);")
    sleep(3)  # Adjust the sleep time if necessary for your page to load content

    # Scrape the main event name
    event_name = driver.find_element(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-max-hbo"]/div[1]/div[1]/div[2]/div/div/h2[1]/strong')
    event_name_text = event_name.text
    events_name.append(event_name_text)

    # Scrape the main description
    description = driver.find_element(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-max-hbo"]/div[1]/div[1]/div[2]/div/div/p[5]/em')
    description_text = description.text
    description_data.append(description_text)

    # Scrape the image URL
    image_element = driver.find_element(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-max-hbo"]/div[1]/div[1]/div[2]/div/div/figure/div/div/picture/img')
    image_url = image_element.get_attribute('src')

    # Scrape other event names and descriptions
    event_names = driver.find_elements(By.TAG_NAME, 'h3')
    print("event_names length:", len(event_names))

    for event in event_names[:3]:  # Limit to the first 3 events
        full_event_name  = event.text
        parts = full_event_name.split('(')
        event_name_text = parts[0].strip()
        date_info_text = parts[1].split(')')[0].strip() if len(parts) > 1 else ''
        print(f"Full Event Name: {full_event_name}")
        print(f"Event Name (before '('): {event_name_text}")
        start_date = date_info_text
        print("start_date : ", start_date)

        # Find the next <p> tag after each event name to get the description
        description_element = event.find_element(By.XPATH, 'following-sibling::p[1]')
        description_text = description_element.text
        print(f"Description: {description_text}")

        # Append event name and description to respective lists
        events_name.append(event_name_text)
        description_data.append(description_text)
        start_date_data.append(start_date)

    # Check that events and descriptions are correctly matched
    print("Events:", events_name)
    print("Descriptions:", description_data)
    print("start_date_data:", start_date_data)
    for start_day in start_date_data:
        print(start_day)

    # Ensure we have an equal number of event names and descriptions
    for i in range(len(events_name)):
        data.append({
            "Image URL": image_url,
            "Event Name": events_name[i],
            "Event Type": "Sale",
            "Event Description": description_data[i],
            "Calendar": "sephora Calendar",
            "All Day": "No",
            "Public/Private": "Public",
            "Reported Count": 0,
            "Start Date": 'start_date',
            "End Date": 'end_date',
        })

    # Close the WebDriver
    driver.quit()

    # Write to CSV file
    with open('events1.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "Image URL", "Event Name", "Event Type", "Event Description",
            "Calendar", "All Day", "Public/Private", "Reported Count",
            "Start Date", "End Date"
        ])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Run the scraper
if __name__ == "__main__":
    xbox_website_data_scraping()
