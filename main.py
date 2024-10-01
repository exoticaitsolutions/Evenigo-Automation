import os
from Integration_With_Bubble.upload_data_in_bubble import *
from Integration_With_Bubble.upload_image_in_bubble import *
from Integration_With_Bubble.bubble_api_integration import *
from SiteUtilsConfig.utils import *
from SiteUtilsConfig.config import *
from MultiWebsiteScraper.sephora_offers_scraper import *
from MultiWebsiteScraper.playstation_website_scraper import *
from MultiWebsiteScraper.hulu_scraper import *
from MultiWebsiteScraper.max_hbo_scraper import *
from MultiWebsiteScraper.netflix_data_scraper import *
from MultiWebsiteScraper.nintendo_website_scraper import *
from MultiWebsiteScraper.prime_data_scraper import *
from MultiWebsiteScraper.xbox_games_scraper import *

def safe_scrape(scrape_function, file_path, calendar_enum):
    """Safely run a scraper, handle file check and send data to Bubble if file exists and is recent."""
    try:
        if os.path.exists(file_path):
            if is_file_older_than(file_path, time_threshold):
                scrape_function()
            else:
                send_csv_data_to_bubble(calendar_enum, file_path)
        else:
            scrape_function()
    except Exception as e:
        print(f"Error while scraping {calendar_enum}: {str(e)}")

any_scraping_done = False  # Flag to track if any scraping was perform

# if WEBSITE.get("SCRAPE_SEPHORA_WEBSITE_OFFERS"):
#     safe_scrape(scrape_sephora_website_offers, file_path, CalendarEnum.SEPHORA.value)
#     any_scraping_done = True

if WEBSITES.get("PRIME_WEBSITE"):
    safe_scrape(scrape_prime_content, prime_file_path, CalendarEnum.PRIME_VIDEO.value)
    any_scraping_done = True

# if WEBSITES.get("XBOX_GAMES_WEBSITE"):
#     safe_scrape(xbox_website_data_scraping, xbox_file_path, CalendarEnum.Xbox_Calendar.value)
#     any_scraping_done = True

# if WEBSITES.get("MAX_HBO_WEBSITE"):
#     safe_scrape(scrape_max_hbo_content, max_hbo_file_path, CalendarEnum.Maxhbo_Calendar.value)
#     any_scraping_done = True

# if WEBSITES.get("NETFLIX_WEBSITE"):
#     safe_scrape(scrape_netflix_content, netflix_file_path, CalendarEnum.NETFLIX.value)
#     any_scraping_done = True          


# if WEBSITES.get("PLAYSTATION_WEBSITE"):
#     safe_scrape(scrape_gamerant_events, playstation_file_path, CalendarEnum.Playstation_Calendar.value)
#     any_scraping_done = True

# if WEBSITES.get("HULU_WEBSITE"):
#     safe_scrape(scrape_hulu_content, hulu_file_path, CalendarEnum.Hulu_Calendar.value)
#     any_scraping_done = True

# if WEBSITES.get("NINTENDO_WEBSITE"):
#     safe_scrape(scrape_nintendo_games, ninten_file_path, CalendarEnum.NINTENDO.value)
#     any_scraping_done = True

# If no scraping was performed, print the message
if not any_scraping_done:
    print("No scraping performed. All the Websites are configured to False.")
