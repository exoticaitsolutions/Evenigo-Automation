
import json
import requests
import csv
import os
from datetime import datetime

# Bubble Data API endpoint and headers
URL = "https://evenigo.com/version-test/api/1.1/obj/event"
CALENDAR_url = "https://evenigo.com/version-test/api/1.1/obj/calendar"
HEADERS = {
    "Authorization": "Bearer 076e0757baab9bbb07df672e8bc751eb",
    "Content-Type": "application/json"
}


# Function to send data to the API and return the ID
def send_data_to_api(data):
    response = requests.post(URL, headers=HEADERS, json=data)
    
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
    "sephora Calendar": "1724393334886x404790430192875300",
}

def get_calendar_id(name):
    return calendar_name_to_id.get(name, None)

def read_and_process_csv(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    ids = []  # Initialize an empty list to store IDs

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
            print("event_type : ", event_type)
            data = {
                "All Day": "yes",
                "End Date/Time (Event)": end_date,
                "Calendar": calendar_id,
                "Event Type": event_type,
                "Event Name": row.get("Event Name"),
                "Public/Private": row.get("Public/Private"),
                "Short Description": row.get("Event Description"),
                "Start Date/Time (Event)": start_date,
                "URL": row.get("Image URL")
            }

            event_id = send_data_to_api(data)  # Send data and get the event ID
            if event_id:
                ids.append(event_id)  # Add the ID to the list

    print(f"All collected IDs: {ids}")  # Print or return the list of IDs
    return ids

def send_data_to_api1(data):
    print(f"Sending data to CALENDAR_url: {data}")
    try:
        # Construct the URL with the specified ID
        url = f'{CALENDAR_url}/1724394041122x749331675895726800'
        
        # Send the PATCH request
        response = requests.patch(url, headers=HEADERS, data=json.dumps(data))
    
        response.raise_for_status()
        
        # Check if the response has content
        if response.status_code == 204:
            print("Response status: 204 No Content. No data returned from server.")
        else:
            # Attempt to parse JSON response if status code is not 204
            try:
                response_data = response.json()
                print(f"Response: {response_data}")
            except ValueError:
                print("Response is not in JSON format or is empty.")
                
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


# Insert events into calendar
def Event_insert(file_path):
    event_list = read_and_process_csv(file_path)
    data = {
        'Name': 'sephora Calendar',
        'Events': event_list  
    }
    
    send_data_to_api1(data)