import os
import csv
from datetime import datetime
import re
from SiteUtilsConfig.utils import (
    clean_data,
    fetch_existing_events,
    validate_and_format_date,
)
from Integration_With_Bubble.bubble_api_integration import *
from urls import *


def fetch_user_id_by_email(email):
    """
    Fetch the user ID based on the email from Bubble.io API.
    Replace this function with actual API integration for fetching user ID.
    """
    return EMAIL_TO_USER_ID_MAP.get(email)

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

    # Ensure existing_events is a list of dictionaries
    if not isinstance(existing_events, list):
        print("Fetched events are not in the expected format. Exiting.")
        return

    # Extract event names from the existing events
    existing_event_names = {
        event.get("Event Name") for event in existing_events if isinstance(event, dict)
    }

    ids = []

    # with open(file_path, mode="r") as file:
    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            print()
            required_fields = [
                "All Day",
                "End Date",
                "Calendar",
                "Event Type",
                "Event Type (text)",
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
            event_type_text = row.get("Event Type (text)")
            default_start_date = datetime.now()
            start_date = validate_and_format_date(
                row.get("Start Date", ""), default_date=default_start_date
            )
            end_date = validate_and_format_date(row.get("End Date", ""))

            if start_date:
                start_date = datetime.strptime(start_date, '%m/%d/%Y') 
                start_date1 = start_date.replace(hour=19, minute=00)
                start_date = start_date1.isoformat()


            if end_date:
                end_date = datetime.strptime(end_date, '%m/%d/%Y')
                end_date1 = end_date.replace(hour=19, minute=00)
                end_date = end_date1.isoformat()

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
                "Event Type (text)": event_type_text,
                "Event Name": clean_data(event_name),
                "Public/Private": row.get("Public/Private"),
                "Short Description": clean_data(row.get("Event Description")),
                "Start Date/Time (Event)": start_date,
                "URL": row.get("Url"),
                "Created By (Edit)": user_id,
            }

            event_id = upload_events_to_bubble_events(data)
            if event_id:
                ids.append(event_id)

    print()
    print("Events Uploaded Successfully in Bubble.io")
    print()
    data = {"Name": CalendarName, "Events": ids}

    upload_events_to_bubble_calendar(CalendarName, data)
    return ids
