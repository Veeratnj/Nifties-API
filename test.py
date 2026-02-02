import json
import csv
import requests
from pathlib import Path

def download_json(url):
    """Download JSON data from URL"""
    print(f"Downloading data from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

def json_to_csv(json_data, output_file):
    """Convert JSON data to CSV"""
    if not json_data:
        print("No data to convert")
        return False
    
    # Handle if json_data is a list or dict
    if isinstance(json_data, dict):
        json_data = [json_data]
    
    if not json_data:
        print("Empty data")
        return False
    
    print(f"Converting {len(json_data)} records to CSV...")
    
    # Get all unique keys from all records
    all_keys = set()
    for record in json_data:
        all_keys.update(record.keys())
    
    fieldnames = sorted(all_keys)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(json_data)
    
    print(f"Successfully created {output_file}")
    print(f"Total records: {len(json_data)}")
    print(f"Total columns: {len(fieldnames)}")
    return True

def convert_from_url(url, output_file='output.csv'):
    """Download JSON from URL and convert to CSV"""
    json_data = download_json(url)
    if json_data:
        return json_to_csv(json_data, output_file)
    return False

def convert_from_file(input_file, output_file='output.csv'):
    """Read JSON from file and convert to CSV"""
    print(f"Reading {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return json_to_csv(json_data, output_file)
    except FileNotFoundError:
        print(f"File not found: {input_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")
        return False

# Main execution
if __name__ == "__main__":
    # NIFTY03FEB2624800CE
    # Angel Broking API URL
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    output_csv = "OpenAPIScripMaster.csv"
    
    # Try to download and convert from URL
    success = convert_from_url(url, output_csv)
    
    # If URL download fails, you can convert from a local file instead
    # Uncomment the line below and comment the line above
    # success = convert_from_file('OpenAPIScripMaster.json', output_csv)
    
    if success:
        print(f"\n✓ Conversion complete! Check {output_csv}")
    else:
        print("\n✗ Conversion failed")
        print("\nIf URL download failed, try:")
        print("1. Download the JSON file manually")
        print("2. Save it in the same folder as this script")
        print("3. Uncomment the convert_from_file() line in the script")