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
    "PRIME_CALENDAR_ID": "1726203559353x851009708434128900",
    "NINENDO_CALENDAR_ID": "1726203618991x966183443157483500",
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
    "PLAYSTATION_WEBSITE": True,
    "HULU_WEBSITE":True,
    "MAX_HBO_WEBSITE":True,
    "NETFLIX_WEBSITE": True,
    "NINTENDO_WEBSITE":True,
    "PRIME_WEBSITE":True,
    "XBOX_GAMES_WEBSITE": True
}