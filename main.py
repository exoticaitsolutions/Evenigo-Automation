import os
from sephora_offers_scraper import scrape_data
from upload_data_in_bubble import *
from upload_image_in_bubble import Event_insert_downloads_images

file_name = 'sephora_beauty_offers.csv'
file_path = get_file_path(file_name)

# Check if the file already exists
if not os.path.exists(file_path):
    print(f"File {file_name} not found. Scraping data...")
    scrape_data()
else:
    print(f"File {file_name} already exists. Skipping data scrape.")

print(f"Checking file path: {file_path}")

Event_insert_downloads_images(file_path)
