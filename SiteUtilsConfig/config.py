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
    "CALENDAR_ID": "1726489371789x199262951906809860",
    "PRIME_CALENDAR_ID": "1726493723471x720073351615339500",
    "NINENDO_CALENDAR_ID": "1726487981417x668703773458943600",
    "NETFLIX_CALENDAR_ID": "1726493636818x380232979441300000",
    "Hulu_CALENDAR_ID": "1726493685107x662944115826212400",
    "Xbox_CALENDAR_ID": "1726487947236x822605360792864500",
    "Playstation_CALENDAR_ID": "1726488074885x374589092089022900",
    "Maxhbo_CALENDAR_ID": "1726546447159x439495280954370400",
}

CALENDAR_NAME_TO_ID = {
    "Sephora Calendar": CALENDAR_ID.get("CALENDAR_ID"),
    "Prime Video": CALENDAR_ID.get("PRIME_CALENDAR_ID"),
    "Nintendo": CALENDAR_ID.get("NINENDO_CALENDAR_ID"),
    "Netflix": CALENDAR_ID.get("NETFLIX_CALENDAR_ID"),
    "Hulu Calendar": CALENDAR_ID.get("Hulu_CALENDAR_ID"),
    "Xbox Calendar": CALENDAR_ID.get("Xbox_CALENDAR_ID"),
    "Playstation Calendar": CALENDAR_ID.get("Playstation_CALENDAR_ID"),
    "Maxhbo Calendar": CALENDAR_ID.get("Maxhbo_CALENDAR_ID"),
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
    "XBOX_GAMES_WEBSITE": True,
    "PRIME_WEBSITE":True
}


time_threshold = 10 * 60
csv_folder_name = 'csv_output'
file_name = "sephora_beauty_offers.csv"
nintendo_file_name = "nintendo_data.csv"
prime_file_name = "Amazon_prime_site.csv"
xbox_file_name = "xbox_games_data.csv"
hulu_file_name = "new_on_hulu.csv"
max_hbo_file_name = "max_hbo_data.csv"
netflix_file_name = "netflix_data.csv"
playstation_file_name = "playstation_website_data.csv"