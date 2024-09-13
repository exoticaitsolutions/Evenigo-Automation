# Headers for uploading data via an API
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
}

CALENDAR_NAME_TO_ID = {
    "sephora Calendar": CALENDAR_ID.get("CALENDAR_ID"),
}
# Configuration flag for scraping offers from the Sephora website
WEBSITE = {
    "SCRAPE_SEPHORA_WEBSITE_OFFERS": True,
}

WEBSITES = {
    "SCRAPE_GAMERANT_WEBSITE": True,
    "SCRAP_HULU_WEBSITE":True,
    "MAX_HBO_WEBSITE":True,
    "NETFLIX_WEBSITE": True,
    "NINTENDO_WEBSITE":True,
    "PRIME_WEBSITE":True,
    "XBOX_GAMES_WEBSITE": True
}