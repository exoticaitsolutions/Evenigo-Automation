import os
import time
from sephora_offers_scraper import *
from upload_data_in_bubble import *
from upload_image_in_bubble import *
from config import *

file_name = 'sephora_beauty_offers.csv'
file_path = get_file_path(file_name)

# Time in seconds (10 minutes)
time_threshold = 10 * 60

def is_file_older_than(file_path, time_threshold):
    if os.path.exists(file_path):
        file_mod_time = os.path.getmtime(file_path)
        current_time = time.time()
        file_age = current_time - file_mod_time
        return file_age > time_threshold
    return False

if website.get('SCRAPE_SEPHORA_WEBSITE_OFFERS'):
    if os.path.exists(file_path):
        if is_file_older_than(file_path, time_threshold):
            os.remove(file_path)
            scrape_sephora_website_offers()
        else:
            upload_images_in_bubble(file_path)
    else:
        scrape_sephora_website_offers()
else:
    print("No scraping performed. SCRAPE_SEPHORA_WEBSITE_OFFERS is set to False.")


