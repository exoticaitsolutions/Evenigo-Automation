import math
import os
from SiteUtilsConfig.utils import DOWNLOAD_FOLDER, save_images_from_csv_to_local_folder
from Integration_With_Bubble.bubble_api_integration import upload_images_to_bubble_events_images
from Integration_With_Bubble.upload_data_in_bubble import send_offers_from_csv_to_api
from SiteUtilsConfig.utils import csv_to_json, check_file_downloaded
import urllib.parse


def send_images_to_bubble_images_api(calendarName, csv_file_path):
    """Read image URLs from a CSV file, download the images, and upload them to Bubble.io.

    Args:
        csv_file_path (str): The path to the CSV file containing image URLs and event details.

    Raises:
        Exception: For errors during processing or image upload.
    """
    event_ids = send_offers_from_csv_to_api(calendarName, csv_file_path)

    # Check if the result is a list and proceed if it's not empty
    if isinstance(event_ids, list) and event_ids:
        print("Processing events and downloading images...")

        event_results = []
        json_data = csv_to_json(csv_file_path)

        if isinstance(json_data, list):
            for i, filedata in enumerate(json_data):
                eventname = filedata.get("Event Name")
                imageurl = filedata.get("Image URL")
                print("imageurl : ", imageurl)
                if not imageurl or (isinstance(imageurl, float) and math.isnan(imageurl)):
                    print(f"No valid image URL for event '{eventname}', skipping...")
                    continue


                # Get the corresponding event ID from the list
                event_id = event_ids[i] if i < len(event_ids) else None
                if event_id is None:
                    print(f"No event ID found for event '{eventname}', skipping...")
                    continue

                filename = os.path.basename(urllib.parse.urlparse(imageurl).path)
                print("--------"*8)
                print("filename : ", filename)
                if not (filename.endswith(".jpg") or filename.endswith(".png")):
                    filename += ".jpg"

                if not check_file_downloaded(DOWNLOAD_FOLDER, filename):
                    save_path = os.path.join(DOWNLOAD_FOLDER, filename)
                    save_images_from_csv_to_local_folder(imageurl, save_path)

                event_results.append(
                    {
                        "EventName": eventname,
                        "eventid": event_id,
                        "save_path": os.path.join(DOWNLOAD_FOLDER, filename),
                    }
                )

            # Upload the event images
            upload_images_to_bubble_events_images(event_results)
        else:
            print("Error or unexpected format returned:", json_data)
    else:
        print("No valid event IDs retrieved or empty list.")
