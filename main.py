import os
from Integration_With_Bubble.upload_data_in_bubble import *
from Integration_With_Bubble.upload_image_in_bubble import *
from Integration_With_Bubble.bubble_api_integration import *
from MultiWebsiteScraper.sephora_offers_scraper import *
from SiteUtilsConfig.utils import *
from  SiteUtilsConfig.config import *
from MultiWebsiteScraper.playstation_website_scraper import *
from MultiWebsiteScraper.hulu_scraper import *
from MultiWebsiteScraper.max_hbo_scraper import *
from MultiWebsiteScraper.netflix_data_scraper import *
from MultiWebsiteScraper.nintendo_website_scraper import *
from MultiWebsiteScraper.prime_data_scraper import *
from MultiWebsiteScraper.xbox_games_scraper import *

if WEBSITE.get("SCRAPE_SEPHORA_WEBSITE_OFFERS"):
    if os.path.exists(file_path):
        if is_file_older_than(file_path, time_threshold):
            scrape_sephora_website_offers()
        else:
            send_images_to_bubble_images_api(CalendarEnum.SEPHORA.value, file_path)
    else:
        scrape_sephora_website_offers()

any_scraping_done = False  # Flag to track if any scraping was performed

if WEBSITES.get("PRIME_WEBSITE"):
    if os.path.exists(prime_file_path):
        if is_file_older_than(prime_file_path, time_threshold):
            scrape_prime_content()
        else:
            send_images_to_bubble_images_api(CalendarEnum.PRIME_VIDEO.value, prime_file_path)
    else:
        scrape_prime_content()
    any_scraping_done = True

if WEBSITES.get("XBOX_GAMES_WEBSITE"):
    if os.path.exists(xbox_file_path):
        if is_file_older_than(xbox_file_path, time_threshold):
            xbox_website_data_scraping()
        else:
            send_images_to_bubble_images_api(CalendarEnum.Xbox_Calendar.value, xbox_file_path)
    else:
        xbox_website_data_scraping()
    any_scraping_done = True

if WEBSITES.get("MAX_HBO_WEBSITE"):
    if os.path.exists(max_hbo_file_path):
        if is_file_older_than(max_hbo_file_path, time_threshold):
            scrape_max_hbo_content()
        else:
            send_images_to_bubble_images_api(CalendarEnum.Maxhbo_Calendar.value, max_hbo_file_path)
    else:
        scrape_max_hbo_content()
    any_scraping_done = True

if WEBSITES.get("NETFLIX_WEBSITE"):
    if os.path.exists(netflix_file_path):
        if is_file_older_than(netflix_file_path, time_threshold):
            scrape_netflix_content()
        else:
            send_images_to_bubble_images_api(CalendarEnum.NETFLIX.value, netflix_file_path)
    else:
        scrape_netflix_content()
    any_scraping_done = True

if WEBSITES.get("PLAYSTATION_WEBSITE"):
    print("Scraping start for playstation website")
    if os.path.exists(playstation_file_path):
        if is_file_older_than(playstation_file_path, time_threshold):
            scrape_gamerant_events()
        else:
            send_images_to_bubble_images_api(CalendarEnum.Playstation_Calendar.value, playstation_file_path)
    else:
        scrape_gamerant_events()
    any_scraping_done = True

if WEBSITES.get("HULU_WEBSITE"):
    if os.path.exists(hulu_file_path):
        if is_file_older_than(hulu_file_path, time_threshold):
            scrape_hulu_content()
        else:
            send_images_to_bubble_images_api(CalendarEnum.Hulu_Calendar.value, hulu_file_path)
    else:
        scrape_hulu_content()
    any_scraping_done = True

if WEBSITES.get("NINTENDO_WEBSITE"):
    if os.path.exists(ninten_file_path):
        if is_file_older_than(ninten_file_path, time_threshold):
            scrape_nintendo_games()
        else:
            send_images_to_bubble_images_api(CalendarEnum.NINTENDO.value, ninten_file_path)
    else:
        scrape_nintendo_games()

    any_scraping_done = True  # Set the flag to True when scraping is performed

# If no scraping was performed, print the message
if not any_scraping_done:
    print("No scraping performed. All the Websites are configured to False.")