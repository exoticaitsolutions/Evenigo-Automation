import uuid
import pandas as pd
import requests
import os
import urllib.parse

# Get the current working directory
current_directory = os.getcwd()

def sanitize_filename(filename):
    """Sanitize the filename to remove or replace invalid characters."""
    # Parse the URL and extract the path component
    filename = os.path.basename(urllib.parse.urlparse(filename).path)
    
    # Replace invalid characters with underscores
    invalid_chars = '<>:\"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    return filename

def download_image(image_url, save_path):
    """Download an image from a URL and save it to a specified path."""
    # Encode the URL to handle special characters
    encoded_url = urllib.parse.quote(image_url, safe=':/?=&')
    
    try:
        response = requests.get(encoded_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  

        # Save the image to a file
        with open(save_path, "wb") as file:
            file.write(response.content)
        
        print(f"Image downloaded successfully and saved to {save_path}.")
    
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    
    except Exception as e:
        print(f"Failed to download image: {e}")

def process_image_csv_download(file_path):
    """Read image URLs from CSV file and download images."""
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='latin1') 
        df.columns = df.columns.str.strip()  
        
        # Print column names for debugging
        print("Columns in CSV file:", df.columns.tolist())
        
        # Check if the expected column exists
        if 'Image URL' not in df.columns:
            print("Error: 'Image URL' column not found in CSV.")
            return
        
        # Create the download folder if it doesn't exist
        download_folder = os.path.join(current_directory, 'download')
        os.makedirs(download_folder, exist_ok=True)
        
        # Iterate over rows and download images
        for index, row in df.iterrows():
            image_url = row['Image URL']  
            if pd.notna(image_url) and image_url.startswith('http'):  
                # Sanitize the filename
                image_name = sanitize_filename(image_url)
                if not image_name:  
                    image_name = f"image_{index}.jpg" 
                
                # Set the full path for saving the image
                save_path = os.path.join(download_folder, image_name)
                download_image(image_url, save_path)
            else:
                print(f"Invalid URL or missing URL at index {index}: {image_url}")

    except Exception as e:
        print(f"An error occurred while processing the CSV file: {e}")



