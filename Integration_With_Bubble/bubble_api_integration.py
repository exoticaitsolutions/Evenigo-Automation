from SiteUtilsConfig.config import *
import requests
import json
import requests
from SiteUtilsConfig.config import UPLOAD_DATA_HEADERS
# from SiteUtilsConfig.utils import image_to_base64
from urls import BUBBLE_CALENDAR_URL, BUBBLE_EVENT_URL

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

def image_to_base64(image_path):
    """Convert an image file to a Base64 encoded string with a MIME type prefix.

    Args:
        image_path (str): The file path of the image to be converted.

    Returns:
        str: The Base64 encoded image string with a MIME type prefix.

    Raises:
        ValueError: If the image file type is unsupported.
    """
    # Determine the image format
    ext = os.path.splitext(image_path)[-1].lower()
    # Open the image file
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img_format = img.format

        # Save the image in its original format to the buffer
        img.save(buffered, format=img_format)
        img_byte_array = buffered.getvalue()
        # Encode the byte array to Base64
        img_base64 = base64.b64encode(img_byte_array).decode("utf-8")

        # Determine the MIME type based on the file extension
        mime_type = ""
        if ext in [".jpeg", ".jpg"]:
            mime_type = "data:image/jpeg;base64,"
        elif ext == ".png":
            mime_type = "data:image/png;base64,"
        else:
            raise ValueError("Unsupported file type: " + ext)

        # Return the full Base64 string with the MIME type prefix
        return mime_type + img_base64


def upload_events_to_bubble_events(data):
    """
    Sends the provided data to the Bubble.io API and returns the ID of the inserted event.

    Args:
        data (dict): The event data to be sent to the API.

    Returns:
        str: The ID of the inserted event, or None if the request failed.
    """
    response = requests.post(BUBBLE_EVENT_URL, headers=UPLOAD_DATA_HEADERS, json=data)

    try:
        response_data = response.json()
    except ValueError:
        response_data = response.text

    if response.status_code == 201:
        print("Data inserted successfully!")
        print(f"Response: {response_data}")
        return response_data.get("id")  # Return the ID from the response
    else:
        print(f"Failed to insert data. Status code: {response.status_code}")
        print(f"Response: {response_data}")
        return None  # Return None if the request failed


def upload_events_to_bubble_calendar(data):
    """
    Sends event IDs to the Bubble.io calendar API.

    Args:
        data (dict): The data containing calendar name and event IDs.

    Returns:
        None
    """
    try:
        url = f"{BUBBLE_CALENDAR_URL}/{CALENDAR_ID.get('CALENDAR_ID')}"

        response = requests.patch(
            url, headers=UPLOAD_DATA_HEADERS, data=json.dumps(data)
        )

        response.raise_for_status()

        if response.status_code == 204:
            print("Data Uploaded Successfully in Calendar Bubble.io.")
            print()
        else:
            try:
                response_data = response.json()
                print(f"Response: {response_data}")
            except ValueError:
                print("Response is not in JSON format or is empty.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def upload_images_to_bubble_events_images(dataarray):
    """Upload images to Bubble.io as Base64 encoded strings.

    Args:
        dataarray (list): List of dictionaries containing event IDs and image paths.

    Raises:
        Exception: For errors during the upload process.
    """
    for multiple in dataarray:
        eventid = multiple["eventid"]
        imgurl = multiple["save_path"]

        # Convert the image to base64
        base64_image = image_to_base64(imgurl)
        payload = {"Image": base64_image, "Original Event": eventid}

        # Prepare the request
        response = requests.post(
            BUBBLE_EVENT_URL, headers=UPLOAD_IMAGES_HEADERS, data=payload
        )

        # Check the response status code
        if response.status_code == 201:
            print(f"Image Uploaded Successfully for Event ID {eventid} in Bubble.io")
        else:
            print(
                f"Failed to upload image for Event ID {eventid}. Status code: {response.status_code}, Response: {response.text}"
            )
