import os
from Integration_With_Bubble.upload_data_in_bubble import *
from Integration_With_Bubble.upload_image_in_bubble import *
from Integration_With_Bubble.bubble_api_integration import *
from MultiWebsiteScraper.sephora_offers_scraper import scrape_sephora_website_offers
from SiteUtilsConfig.config import *
from SiteUtilsConfig.utils import *
from  SiteUtilsConfig.config import *
from MultiWebsiteScraper.playstation_website_scraper import *
from MultiWebsiteScraper.hulu_scraper import *
from MultiWebsiteScraper.max_hbo_scraper import *
from MultiWebsiteScraper.netflix_data_scraper import *
from MultiWebsiteScraper.nintendo_website_scraper import *
from MultiWebsiteScraper.prime_data_scraper import *
from MultiWebsiteScraper.xbox_games_scraper import xbox_website_data_scraping

if WEBSITE.get("SCRAPE_SEPHORA_WEBSITE_OFFERS"):
    if os.path.exists(file_path):
        if is_file_older_than(file_path, time_threshold):
            # os.remove(file_path)
            scrape_sephora_website_offers()
        else:
            send_images_to_bubble_images_api(file_path)
    else:
        scrape_sephora_website_offers()

if WEBSITES.get("NINTENDO_WEBSITE"):
    scrape_nintendo_games()

if WEBSITES.get("PRIME_WEBSITE"):
    scrape_prime_content()

# if WEBSITES.get("HULU_WEBSITE"):
#     scrape_hulu_content()

# if WEBSITES.get("MAX_HBO_WEBSITE"):
#     scrape_max_hbo_content()

# if WEBSITES.get("NETFLIX_WEBSITE"):
#     scrape_netflix_content()


# if WEBSITES.get("XBOX_GAMES_WEBSITE"):
#     xbox_website_data_scraping()

# if WEBSITES.get("PLAYSTATION_WEBSITE"):
#     scrape_gamerant_events()

else:
    print("No scraping performed. SCRAPE_SEPHORA_WEBSITE_OFFERS is set to False.")

