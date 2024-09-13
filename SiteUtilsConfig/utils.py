from datetime import datetime
import base64
import re
import time
from PIL import Image
from io import BytesIO
import urllib.parse
import os
import pandas as pd
from datetime import datetime
import requests
from Integration_With_Bubble .bubble_api_integration import *
from urls import *
from SiteUtilsConfig.config import *


# Define the download folder path
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
# Time in seconds (10 minutes)
time_threshold = 10 * 60
file_name = "sephora_beauty_offers.csv"


# Check if the folder exists, and if not, create it
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
    print(f"Created directory: {DOWNLOAD_FOLDER}")


def get_file_path(file_name):
    """
    Constructs the file path for the given file name in the current directory.

    Args:
        file_name (str): The name of the file.

    Returns:
        str: The full file path.
    """
    current_directory = os.getcwd()
    return os.path.join(current_directory, file_name)


def validate_and_format_date(date_str, default_date=None):
    """
    Validates and formats a date string to the required format.

    Args:
        date_str (str): The date string to validate and format.
        default_date (datetime, optional): The default date to use if date_str is empty.

    Returns:
        str: The formatted date string in mm/dd/yyyy, or None if the format is invalid.
    """
    # Define date formats
    date_formats = [
        "%Y-%m-%d %H:%M:%S",  # e.g., 2024-08-29 14:30:00
        "%Y-%m-%d",  # e.g., 2024-08-29
        "%d/%m/%Y",  # e.g., 29/08/2024
        "%m/%d/%Y",  # e.g., 08/29/2024
        "%d-%m-%Y",  # e.g., 29-08-2024
        "%d %b %Y",  # e.g., 29 Aug 2024
        "%b %d %Y",  # e.g., Aug 29 2024
        "%d %B %Y",  # e.g., 29 August 2024
        "%B %d %Y",  # e.g., August 29 2024
        "%m/%d/%Y",  # e.g., 08/29/2024 (added to match mm/dd/yyyy format)
    ]

    # Handle empty string and use default_date if provided
    if date_str.strip() == "" and default_date:
        return default_date.strftime("%m/%d/%Y")

    # Attempt to parse and format the date string
    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_str, date_format)
            return date_obj.strftime("%m/%d/%Y")
        except ValueError:
            continue

    # Return None if no valid date format is found
    return None


special_characters = r"[¶•§§\^\*†‡‡â€¡â€¡稚熔容痴熔®â€™â€™]"


def clean_description(description):
    return re.sub(special_characters, "", description)


def get_calendar_id(name):
    return CALENDAR_NAME_TO_ID.get(name, None)

def fetch_existing_events():
    """
    Fetches the existing events from the Bubble.io API.

    Returns:
        list: A list of existing event data, or an empty list if an error occurs.
    """
    try:
        response = requests.get(BUBBLE_EVENT_URL, headers=UPLOAD_DATA_HEADERS)
        response.raise_for_status()

        try:
            response_data = response.json()

            # Extract the actual event data from the nested response
            events = response_data.get("response", {}).get("results", [])
            if not isinstance(events, list):
                print("The 'results' field is not a list. Exiting.")
                return []
            return events
        except ValueError:
            print("Response is not in JSON format.")
            return []
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return []
    except Exception as err:
        print(f"Other error occurred: {err}")
        return []


def csv_to_json(csv_file_path):
    """
    Converts a CSV file to JSON format.

    Args:
        csv_file_path (str): The path to the CSV file.

    Returns:
        list or str: The JSON data if successful, otherwise an error message.
    """
    try:
        df = pd.read_csv(csv_file_path)

        json_data = df.to_dict(orient="records")
        return json_data
    except FileNotFoundError:
        return f"Error: The file {csv_file_path} was not found."
    except pd.errors.EmptyDataError:
        return "Error: The CSV file is empty."
    except pd.errors.ParserError:
        return "Error: There was a problem parsing the CSV file."
    except Exception as e:
        return f"An unexpected error occurred: {e}"


def check_file_downloaded(download_dir: str, filename: str) -> bool:
    """
    Checks if the specified file has been downloaded to the given directory.

    Args:
        download_dir (str): The path to the directory where the file should be.
        filename (str): The name of the file to check for.

    Returns:
        bool: True if the file is found in the directory, False otherwise.
    """
    files = os.listdir(download_dir)
    if filename in files:
        return True
    return False


def save_images_from_csv_to_local_folder(image_url, save_path):
    """Download an image from a URL and save it to a specified path.

    Args:
        image_url (str): The URL of the image to download.
        save_path (str): The file path where the image should be saved.

    Raises:
        requests.HTTPError: If an HTTP error occurs during the download.
        Exception: For other errors during the image download process.
    """
    # Encode the URL to handle special characters
    encoded_url = urllib.parse.quote(image_url, safe=":/?=&")

    try:
        response = requests.get(encoded_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        # Save the image to a file
        with open(save_path, "wb") as file:
            file.write(response.content)

    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")

    except Exception as e:
        print(f"Failed to download image: {e}")


file_path = get_file_path(file_name)


def is_file_older_than(file_path, time_threshold):
    if os.path.exists(file_path):
        file_mod_time = os.path.getmtime(file_path)
        current_time = time.time()
        file_age = current_time - file_mod_time
        return file_age > time_threshold
    return False
