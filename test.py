import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import re

# URL to scrape
url = 'https://www.tvguide.com/news/new-on-max-hbo/'

# Send the request to fetch the webpage
response = requests.get(url)
data = []

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    shortcode_content_div = soup.find('div', class_='c-ShortcodeContent')

    all_content = []
    event_name = ""
    img_tag_src = ""

    # Get today's date and one day later for default start and end dates
    today = datetime.today().strftime('%Y-%m-%d')
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    if shortcode_content_div:
        # Extract the first h2 strong tag if available (First event)
        first_h2_strong = shortcode_content_div.find('h2').strong if shortcode_content_div.find('h2') else None
        if first_h2_strong:
            event_name = first_h2_strong.get_text(strip=True)

            # Extract the date from the event name if present in parentheses
            match = re.search(r'\((.*?)\)', event_name)
            if match:
                start_date = match.group(1)
            else:
                start_date = today  # Default to today's date
            end_date = tomorrow  # Default to tomorrow's date
            
        # Extract the image from the first figure
        first_figure = shortcode_content_div.find('figure')
        if first_figure:
            img_tag = first_figure.find('img')
            if img_tag:
                img_tag_src = img_tag['src']  # Save the image URL for later
                print("img_tag : ", img_tag_src)
                data.append({
                    "Image URL": img_tag_src,
                    "Event Name": event_name,
                    "Event Type": "Sale",
                    "Event Description": '',
                    "Calendar": "sephora Calendar",
                    "All Day": "No",
                    "Public/Private": "Public",
                    "Reported Count": 0,
                    "Start Date": start_date,
                    "End Date": end_date,
                })

        h2_elements = shortcode_content_div.find_all('h2')

        third_h2 = h2_elements[2] if len(h2_elements) >= 3 else None

        siblings = []
        skip_first_p = False
        skip_first_ul = False

        # Collect siblings after the first figure
        for sibling in first_figure.find_next_siblings():
            if sibling.name == 'div' and 'c-commercePromo' in sibling.get('class', []):
                skip_first_p = True
                skip_first_ul = True
                continue
            if skip_first_p and sibling.name == 'p':
                skip_first_p = False
                continue
            if skip_first_ul and sibling.name == 'ul':
                skip_first_ul = False
                continue
            if sibling == third_h2:
                break
            siblings.append(sibling)

        # Process siblings to extract event details
        for sibling in siblings:
            event_name = ""
            if sibling.name in ['h2', 'h3', 'strong']:
                event_name = sibling.get_text(strip=True)

                # Extract the date from the event name if present in parentheses
                match = re.search(r'\((.*?)\)', event_name)
                if match:
                    start_date = match.group(1)
                    start_date = start_date.split(',')[0].strip()
                    event_name1 = event_name.replace(match.group(0), '').strip()
                else:
                    start_date = today  # Default to today's date
                end_date = tomorrow  # Default to tomorrow's date
                
                # Append the event details into data
                data.append({
                    "Image URL": '',  # Using the saved image URL
                    "Event Name": event_name1,
                    "Event Type": "Sale",
                    "Event Description": '',
                    "Calendar": "sephora Calendar",
                    "All Day": "No",
                    "Public/Private": "Public",
                    "Reported Count": 0,
                    "Start Date": start_date,
                    "End Date": end_date,
                })
            link = "" 
            sibling_text = ""
            image = ""
      
            for part in sibling.descendants:
                if part.name == 'a' and part.get('href'):
                    link_text = part.get_text(strip=True)
                    link_href = part['href']
                    link += f"{link_text}({link_href})\n"
                elif part.name == 'img' and part.get('src'):
                    image = part['src']
                elif part.name in ['p', 'li', 'br']:
                    sibling_text += "\n"
                elif part.name is None:
                    sibling_text += part.strip() + " "
            print("----------------------------------------"*4)
            description = sibling_text.strip()
            print()
            print(" description : ", description)
            print()
            print("----------------------------------------"*4)
            link = link.strip()
            print("link : ", link)
            print("image : ", image)

#             # all_content.append([event_name1, description.strip(), link.strip(), image])
#     # Write to CSV file
#     with open('events.csv', mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.DictWriter(file, fieldnames=[
#             "Image URL", "Event Name", "Event Type", "Event Description",
#             "Calendar", "All Day", "Public/Private", "Reported Count",
#             "Start Date", "End Date"
#         ])
#         writer.writeheader()
#         for row in data:
#             writer.writerow(row)

#     print("CSV file 'events.csv' created successfully!")

# else:
#     print('Failed to retrieve the page')
