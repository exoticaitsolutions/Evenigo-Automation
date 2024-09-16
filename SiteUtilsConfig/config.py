# Headers for uploading data via an API
import os
from enum import Enum


UPLOAD_DATA_HEADERS = {
    "Authorization": "Bearer 076e0757baab9bbb07df672e8bc751eb",
    "Content-Type": "application/json",
}

# Headers for uploading images via an API
UPLOAD_IMAGES_HEADERS = {
    "Authorization": UPLOAD_DATA_HEADERS["Authorization"],
}

# Containing a calendar ID for scheduling or event purposes
CALENDAR_ID = {
    "CALENDAR_ID": "1724394041122x749331675895726800",
    "PRIME_CALENDAR_ID": "1726203559353x851009708434128900",
    "NINENDO_CALENDAR_ID": "1726322856020x274189297805784930",
    "NETFLIX_CALENDAR_ID": "1726203580715x697850244902682600",
}

CALENDAR_NAME_TO_ID = {
    "sephora Calendar": CALENDAR_ID.get("CALENDAR_ID"),
    "Prime Video": CALENDAR_ID.get("PRIME_CALENDAR_ID"),
    "Nintendo": CALENDAR_ID.get("NINENDO_CALENDAR_ID"),
    "Netflix": CALENDAR_ID.get("NETFLIX_CALENDAR_ID"),
}

# Configuration flag for scraping offers from the Sephora website
WEBSITE = {
    "SCRAPE_SEPHORA_WEBSITE_OFFERS": True,
}

WEBSITES = {
    "PLAYSTATION_WEBSITE": False,
    "HULU_WEBSITE":False,
    "MAX_HBO_WEBSITE":False,
    "NETFLIX_WEBSITE": True,
    "NINTENDO_WEBSITE":False,
    #Data insertion working in Bubble.
    "XBOX_GAMES_WEBSITE": True,
    "PRIME_WEBSITE":False
}

FILE_TYPE = 'csv'
FILE_NAME={
    "PLAYSTATION_WEBSITE": f'nintendo_data.{FILE_TYPE}',
    "HULU_WEBSITE":f'new_on_hulu.{FILE_TYPE}',
    "MAX_HBO_WEBSITE":f'max_hbo_data.{FILE_TYPE}',
    "NETFLIX_WEBSITE": f'netflix_data.{FILE_TYPE}',
    "SEPHORA_WEBSITE": f'sephora_beauty_offers.{FILE_TYPE}',
    #Data insertion working in Bubble.
    "XBOX_GAMES_WEBSITE": f'xbox_games_data.{FILE_TYPE}',
    "PRIME_WEBSITE":f'Amazon_prime_site.{FILE_TYPE}'
}

# Define the download folder path
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
# Time in seconds (10 minutes)
time_threshold = 10 * 60
FILE_PATH = 'csv_output'
os.makedirs(FILE_PATH, exist_ok=True)  # Create folder if it doesn't exist


class CalendarEnum(Enum):
    SEPHORA = 'sephora Calendar'
    PRIME_VIDEO = 'Prime Video'
    NINTENDO = 'Nintendo'
    NETFLIX = 'Netflix'

PRIME_WEBSITE_URL   = 'https://www.tvguide.com/news/new-on-amazon-prime-video/'

