import os
from upload_data_in_buble import *
from scraper import *
from download_image import *

# Get the current working directory
scrape_data()
current_directory = os.getcwd()
file_name = 'sephora_beauty_offers.csv'
file_path = os.path.join(current_directory, file_name)
print(f"Checking file path: {file_path}")
Event_insert(file_path)
# process_image_csv_download(file_path)
