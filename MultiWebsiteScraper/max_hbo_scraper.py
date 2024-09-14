from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from seleniumbase import Driver
from time import sleep
import csv
import os
from urls import NEW_ON_MAX_HBO_WEBSITE_URL

data = []
events_name = []
description_data = []
start_date_data = []

def parse_date(start_date_data):
    month_map = {
        'Jan': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Apr', 'May': 'May', 'Jun': 'Jun',
        'Jul': 'Jul', 'Aug': 'Aug', 'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dec': 'Dec',
        'Sept': 'Sep',  # Handle common variations
        'September': 'Sep'
    }

    formatted_dates = []
    for start_day in start_date_data:
        # Remove "HBO" and trim after the comma
        clean_start_day = start_day.split(',')[0].replace('HBO', '').strip()

        # Remove the period after the month if present (e.g., "Sept." -> "Sept")
        clean_start_day = clean_start_day.replace('.', '')

        # Replace month abbreviation with the correct format
        month_day = clean_start_day.split(' ')
        if month_day[0] in month_map:
            month_day[0] = month_map[month_day[0]]
        clean_start_day = ' '.join(month_day)

        try:
            # Parse the month name and day
            parsed_date = datetime.strptime(clean_start_day, '%b %d')

            # Replace the year with the current year
            current_year = datetime.now().year
            start_date = parsed_date.replace(year=current_year)

            # Calculate end date (7 days later)
            end_date = start_date + timedelta(days=7)

            # Format the start and end dates as 'dd-mm-yyyy'
            formatted_start_date = start_date.strftime('%d-%m-%Y')
            formatted_end_date = end_date.strftime('%d-%m-%Y')

            formatted_dates.append((formatted_start_date, formatted_end_date))
        except ValueError:
            print(f"Could not parse date: {clean_start_day}")
            formatted_dates.append(('', ''))  # Append empty strings if parsing fails

    return formatted_dates

def scrape_max_hbo_content():
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
    # events_name.append(event_name_text)

    # Scrape the main description
    description = driver.find_element(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-max-hbo"]/div[1]/div[1]/div[2]/div/div/p[5]/em')
    description_text = description.text
    # description_data.append(description_text)

    # Scrape the image URL
    image_element = driver.find_element(By.XPATH, '//*[@id="c-pageArticleSingle-new-on-max-hbo"]/div[1]/div[1]/div[2]/div/div/figure/div/div/picture/img')
    image_url = image_element.get_attribute('src')
    data.append({
            "Event Name": event_name_text,
            "Event Type": "Event",
            "Event Description": description_text,
            "Calendar": "Max_hbo Calendar",
            "All Day": "No",
            "Public/Private": "Public",
            "Reported Count": 0,
            "Start Date": '',
            "End Date": '',
            "Created By": '',
            "URL": NEW_ON_MAX_HBO_WEBSITE_URL,
            "Image URL": image_url,
        })

    # Scrape other event names and descriptions
    event_names = driver.find_elements(By.TAG_NAME, 'h3')

    for event in event_names[:3]:  # Limit to the first 3 events
        full_event_name = event.text
        parts = full_event_name.split('(')
        event_name_text = parts[0].strip()
        date_info_text = parts[1].split(')')[0].strip() if len(parts) > 1 else ''
        start_date = date_info_text

        # Find the next <p> tag after each event name to get the description
        description_element = event.find_element(By.XPATH, 'following-sibling::p[1]')
        description_text = description_element.text

        # Append event name and description to respective lists
        events_name.append(event_name_text)
        description_data.append(description_text)
        start_date_data.append(start_date)

    # Parse dates and calculate end dates
    parsed_dates = parse_date(start_date_data)

    # Ensure we have an equal number of event names and descriptions
    for i in range(len(events_name)):
        start_date, end_date = parsed_dates[i] if i < len(parsed_dates) else ('', '')
        data.append({
            "Event Name": events_name[i],
            "Event Type": "Event",
            "Event Description": description_data[i],
            "Calendar": "Max_hbo Calendar",
            "All Day": "No",
            "Public/Private": "Public",
            "Reported Count": 0,
            "Start Date": start_date,
            "End Date": end_date,
            "Created By": '',
            "URL": NEW_ON_MAX_HBO_WEBSITE_URL,
            "Image URL": '',
        })
    
    month_mapping = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }

    for i in range(11, 35):
        description_element = driver.find_element(By.XPATH, f'//*[@id="c-pageArticleSingle-new-on-max-hbo"]/div[1]/div[1]/div[2]/div/div/p[{i}]')
        description = description_element.text
        
        # Extract date
        parts = description.split()
        if len(parts) >= 2:
            month_name = parts[0]
            day = parts[1].split(',')[0]
            day = day.zfill(2)
            month_number = month_mapping.get(month_name)
            
            if month_number:
                year = datetime.now().year
                # Create a datetime object for the start date
                start_date_str = f"{day}-{month_number}-{year}"
                start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
                
                # Compute the end date
                end_date = start_date + timedelta(days=7)
                end_date_str = end_date.strftime("%d-%m-%Y")
                
                # Prepare data for appending
                desc = "\n".join(description.split("\n")[1:])
                data.append({
                    "Event Name": desc,
                    "Event Type": "Event",
                    "Event Description": '',
                    "Calendar": "Max_hbo Calendar",
                    "All Day": "No",
                    "Public/Private": "Public",
                    "Reported Count": 0,
                    "Start Date": start_date_str,
                    "End Date": end_date_str,
                    "Created By": '',
                    "URL": NEW_ON_MAX_HBO_WEBSITE_URL,
                    "Image URL": '',
                })
            else:
                print(f"Invalid month name: {month_name}")
        else:
            print(f"Description format is not as expected: {description}")

    # Close the WebDriver
    driver.quit()

    # Define the folder and CSV file path
    folder_path = 'csv_output'
    os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist
    csv_file_path = os.path.join(folder_path, 'max_hbo_data.csv')

    # Write to CSV file
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "Event Name", "Event Type", "Event Description", "Calendar", "All Day", "Public/Private",
            "Reported Count", "Start Date", "End Date", "Image URL", "Created By", "URL"
        ])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"Data has been written to {csv_file_path}")

# Run the scraper
if __name__ == "__main__":
    scrape_max_hbo_content()