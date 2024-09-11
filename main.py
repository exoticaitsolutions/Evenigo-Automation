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

# if WEBSITES.get("MAX_HBO_WEBSITE"):
#     scrape_max_hbo_content()

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

else:
    print("No scraping performed. SCRAPE_SEPHORA_WEBSITE_OFFERS is set to False.")