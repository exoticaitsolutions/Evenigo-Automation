
import json
import requests
import csv
import os
from datetime import datetime
import base64
from PIL import Image
from io import BytesIO

from download_image import *
from upload_data_in_bubble import *

Image_upload_URL = "https://evenigo.com/version-test/api/1.1/obj/Event-image"
import os

# Define the download folder path
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")

# Check if the folder exists, and if not, create it
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
    print(f"Created directory: {DOWNLOAD_FOLDER}")
    
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")

def image_to_base64(image_path):
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
        img_base64 = base64.b64encode(img_byte_array).decode('utf-8')

        # Determine the MIME type based on the file extension
        mime_type = ""
        if ext in ['.jpeg', '.jpg']:
            mime_type = "data:image/jpeg;base64,"
        elif ext == '.png':
            mime_type = "data:image/png;base64,"
        else:
            raise ValueError("Unsupported file type: " + ext)
        
        # Return the full Base64 string with the MIME type prefix
        return mime_type + img_base64
    
def Event_insert_downloads_images(csv_file_path):

    # Call `read_and_process_csv` once to get the list of event IDs
    event_ids = read_and_process_csv(csv_file_path)

    # Check if the result is a list and proceed if it's not empty
    if isinstance(event_ids, list) and event_ids:
        print("Processing events and downloading images...")

        event_results = []
        json_data = csv_to_json(csv_file_path)

        if isinstance(json_data, list):
            for i, filedata in enumerate(json_data):
                print(f"Processing event {i + 1} of {len(json_data)}")
                eventname = filedata.get('Event Name')
                imageurl = filedata.get('Image URL')

                # Get the corresponding event ID from the list
                event_id = event_ids[i] if i < len(event_ids) else None
                if event_id is None:
                    print(f"No event ID found for event '{eventname}', skipping...")
                    continue

                filename = os.path.basename(urllib.parse.urlparse(imageurl).path)
                
                if not check_file_downloaded(DOWNLOAD_FOLDER, filename):
                    save_path = os.path.join(DOWNLOAD_FOLDER, filename)
                    download_image(imageurl, save_path)

                event_results.append({
                    "EventName": eventname,
                    "eventid": event_id,
                    "save_path": os.path.join(DOWNLOAD_FOLDER, filename),
                })
            
            # Upload the event images
            Event_Image_upload1(event_results)
        else:
            print("Error or unexpected format returned:", json_data)
    else:
        print("No valid event IDs retrieved or empty list.")


def Event_Image_upload1(dataarray):
    HEADERS1 = {
    "Authorization": "Bearer 076e0757baab9bbb07df672e8bc751eb",
    # "Content-Type": "application/json"
}
    for multiple in dataarray:
        eventid = multiple['eventid']
        imgurl = multiple['save_path']
        print('image : ', imgurl)
        base64_image = image_to_base64(imgurl)
        payload = {'Image':base64_image,'Original Event': eventid}
        files=[

        ]
        response = requests.request("POST", Image_upload_URL, headers=HEADERS1, data=payload, files=files)
        print('response', response.text)
    print("Image Uploaded Succesfully In Bubble.io")
     
