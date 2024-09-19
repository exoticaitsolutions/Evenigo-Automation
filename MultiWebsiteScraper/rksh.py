import os
import csv
from datetime import datetime
import re
from SiteUtilsConfig.utils import clean_description, fetch_existing_events, get_calendar_id, validate_and_format_date
from Integration_With_Bubble.bubble_api_integration import *
from urls import *

def fetch_user_id_by_email(email):
    """
    Fetch the user ID based on the email from Bubble.io API.
    Replace this function with actual API integration for fetching user ID.
    """
    email_to_user_id_map = {
        "evenigoofficial+1212@gmail.com": "1725406841796x621130586024924800", 
        "evenigoofficial+6@gmail.com": "1724110723458x455625403407267100",
    }
    return email_to_user_id_map.get(email)


def send_offers_from_csv_to_api(CalendarName, file_path):
    """
    Reads and processes a CSV file, then sends the data to the API.
    Args:
        file_path (str): The path to the CSV file.
    Returns:
        list: A list of IDs of the inserted events.
    """
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return
    existing_events = fetch_existing_events()
    if not isinstance(existing_events, list):
        print("Fetched events are not in the expected format. Exiting.")
        return
    existing_event_names = {
        event.get("Event Name") for event in existing_events if isinstance(event, dict)
    }

    ids = []
    # calander_ids = []

    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            print()
            default_start_date = datetime.now()
            required_fields = [
                "All Day",
                "End Date",
                "Calendar",
                "Event Type",
                "Reported Count",
                "Event Name",
                "Public/Private",
                "Event Description",
                "Image URL",
                "Created By",
            ]
            
            if not all(field in row for field in required_fields):
                print()
                print(f"Skipping row due to missing fields: {row}")
                print()
                continue
            calendar_id = CALENDAR_NAME_TO_ID.get(CalendarName)

            if not calendar_id:
                print(f"Skipping row due to invalid Calendar ID: {row}")
                continue
            event_type = row.get("Event Type")
            valid_event_types = ["Sale"]
            if event_type not in valid_event_types:
                print(f"Skipping row due to invalid Event Type: {event_type}")
                continue
            start_date = validate_and_format_date(
                row.get("Start Date", ""), default_date=default_start_date
            )
            end_date = validate_and_format_date(row.get("End Date", ""))

            # if start_date is None or end_date is None:
            #     print(f"Skipping row due to invalid date format: {row}")
            #     continue

            event_name = row.get("Event Name")
            if event_name in existing_event_names:
                print(f"Skipping row due to existing event: {event_name}")
                continue
            
            created_by_email = row.get("Created By")
            user_id = fetch_user_id_by_email(created_by_email)

            data = {
                "All Day": "yes",
                "End Date/Time (Event)": end_date,
                "Calendar": calendar_id,
                "Event Type": event_type,
                "Event Name": event_name,
                "Public/Private": row.get("Public/Private"),
                # "Short Description": clean_description(row.get("Event Description")),
                "Short Description": row.get("Event Description"),
                "Start Date/Time (Event)": start_date,
                "URL": row.get("Url"),
                "Created By (Edit)": user_id,
            }
            print("print data in sephora ========================>",data)
            event_id = upload_events_to_bubble_events(data)
            if event_id:
                ids.append(event_id)

    print()
    print("Events Uploaded Successfully in Bubble.io")
    print()
    data = {"Name": CalendarName, "Events": ids}
    upload_events_to_bubble_calendar(CalendarName, data)
    return ids