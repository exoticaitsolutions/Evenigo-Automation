import os
from sephora_offers_scraper import *
from upload_data_in_bubble import *
from upload_image_in_bubble import send_images_to_bubble_images_api
from config import *
from utils import *
from config import *
from gamerant_website_scraper import *
from hulu_scraper import *
from max_hbo_scraper import *
from netflix_data_scraper import *
from nintendo_website_scraper import *
from prime_data_scraper import *
from xbox_games_scraper import xbox_website_data_scraping


if WEBSITES.get("SCRAP_HULU_WEBSITE"):
    scrape_hulu_content()

if WEBSITES.get("MAX_HBO_WEBSITE"):
    scrape_max_hbo_content()

if WEBSITES.get("NETFLIX_WEBSITE"):
    scrape_netflix_content()

if WEBSITES.get("NINTENDO_WEBSITE"):
    scrape_nintendo_games()

if WEBSITES.get("PRIME_WEBSITE"):
    scrape_prime_content()

if WEBSITES.get("XBOX_GAMES_WEBSITE"):
    xbox_website_data_scraping()

if WEBSITES.get("SCRAPE_GAMERANT_WEBSITE"):
    scrape_gamerant_events()

if WEBSITE.get("SCRAPE_SEPHORA_WEBSITE_OFFERS"):
    if os.path.exists(file_path):
        if is_file_older_than(file_path, time_threshold):
            # os.remove(file_path)
            scrape_sephora_website_offers()
        else:
            send_images_to_bubble_images_api(file_path)
    else:
        scrape_sephora_website_offers()
else:
    print("No scraping performed. SCRAPE_SEPHORA_WEBSITE_OFFERS is set to False.")

