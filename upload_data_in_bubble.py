import os
import csv
from datetime import datetime
import re
from utils import *
from bubble_api_integration import *
from sephora_urls import *
from config import *


def send_offers_from_csv_to_api(file_path):
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

    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)

        for row in reader:
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
            ]
            if not all(field in row for field in required_fields):
                print(f"Skipping row due to missing fields: {row}")
                continue
            calendar_id = get_calendar_id(row.get("Calendar"))
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

            if start_date is None or end_date is None:
                print(f"Skipping row due to invalid date format: {row}")
                continue

            event_name = row.get("Event Name")
            if event_name in existing_event_names:
                print(f"Skipping row due to existing event: {event_name}")
                continue
            data = {
                "All Day": "yes",
                "End Date/Time (Event)": end_date,
                "Calendar": calendar_id,
                "Event Type": event_type,
                "Event Name": event_name,
                "Public/Private": row.get("Public/Private"),
                # "Short Description": row.get("Event Description"),
                "Short Description": clean_description(row.get("Event Description")),
                "Start Date/Time (Event)": start_date,
                "URL": row.get("Url"),
            }

            event_id = upload_events_to_bubble_events(data)
            if event_id:
                ids.append(event_id)

    print()
    print("Events Uploaded Successfully in Bubble.io")
    print()
    data = {"Name": "sephora Calendar", "Events": ids}

    upload_events_to_bubble_calendar(data)
    return ids
