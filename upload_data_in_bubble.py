import os
import pandas as pd
import json
import requests
import csv
from datetime import datetime
from sephora_urls import *

# Bubble Data API endpoint and headers
HEADERS = {
    "Authorization": "Bearer 076e0757baab9bbb07df672e8bc751eb",
    "Content-Type": "application/json"
}

# Function to send data to the API and return the ID
def send_data_to_api(data):
    response = requests.post(BUBBLE_EVENT_URL, headers=HEADERS, json=data)
    
    try:
        response_data = response.json()
    except ValueError:
        response_data = response.text

    if response.status_code == 201:
        print("Data inserted successfully!")
        print(f"Response: {response_data}")
        return response_data.get('id')  # Return the ID from the response
    else:
        print(f"Failed to insert data. Status code: {response.status_code}")
        print(f"Response: {response_data}")
        return None  # Return None if the request failed

def get_file_path(file_name):
    current_directory = os.getcwd()
    return os.path.join(current_directory, file_name)

def validate_and_format_date(date_str, default_date=None):
    date_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]

    if date_str.strip() == "" and default_date:
        return default_date.strftime("%Y-%m-%dT%H:%M:%S")

    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_str, date_format)
            return date_obj.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue

    return None

calendar_name_to_id = {
    "sephora Calendar": CALENDAR_ID,
}

def send_data_to_calander_api1(data):
    try:
        url = f'{BUBBLE_CALENDAR_URL}/{CALENDAR_ID}'
        
        response = requests.patch(url, headers=HEADERS, data=json.dumps(data))
    
        response.raise_for_status()
        
        if response.status_code == 204:
            print("Response status: 204 No Content. No data returned from server.")
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

def get_calendar_id(name):
    return calendar_name_to_id.get(name, None)

def fetch_existing_events():
    try:
        response = requests.get(BUBBLE_EVENT_URL, headers=HEADERS)
        response.raise_for_status()
        
        try:
            response_data = response.json()
            
            # Extract the actual event data from the nested response
            events = response_data.get('response', {}).get('results', [])
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


def read_and_process_csv(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    existing_events = fetch_existing_events()
    
    # Ensure existing_events is a list of dictionaries
    if not isinstance(existing_events, list):
        print("Fetched events are not in the expected format. Exiting.")
        return
    
    # Extract event names from the existing events
    existing_event_names = {event.get('Event Name') for event in existing_events if isinstance(event, dict)}

    ids = []

    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            default_start_date = datetime.now()
            required_fields = ["All Day", "End Date", "Calendar", "Event Type", "Reported Count", "Event Name", "Public/Private", "Event Description", "Image URL"]
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
            start_date = validate_and_format_date(row.get("Start Date", ""), default_date=default_start_date)
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
                "Short Description": row.get("Event Description"),
                "Start Date/Time (Event)": start_date,
                "URL": row.get("Image URL")
            }

            event_id = send_data_to_api(data)
            if event_id:
                ids.append(event_id)

    print()
    print("Events Uploaded Successfully in Bubble.io")
    print()
    data = {
        'Name': 'sephora Calendar',
        'Events': ids  
    }
    
    send_data_to_calander_api1(data)
    print()
    print("Data Uploaded Successfully in Calendar Bubble.io")
    print()
    return ids


def csv_to_json(csv_file_path):
    try:
        df = pd.read_csv(csv_file_path)
        
        json_data = df.to_dict(orient='records')
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
