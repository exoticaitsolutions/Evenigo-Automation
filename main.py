import os
from sephora_offers_scraper import *
from upload_data_in_bubble import *
from upload_image_in_bubble import send_images_to_bubble_images_api
from config import *
from utils import *


if WEBSITE.get("SCRAPE_SEPHORA_WEBSITE_OFFERS"):
    if os.path.exists(file_path):
        if is_file_older_than(file_path, time_threshold):
            os.remove(file_path)
            scrape_sephora_website_offers()
        else:
            send_images_to_bubble_images_api(file_path)
    else:
        scrape_sephora_website_offers()
else:
    print("No scraping performed. SCRAPE_SEPHORA_WEBSITE_OFFERS is set to False.")
