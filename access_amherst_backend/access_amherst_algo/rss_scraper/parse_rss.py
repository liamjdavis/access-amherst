import xml.etree.ElementTree as ET
import json
from datetime import datetime
from access_amherst_algo.models import Event  # Import the Event model
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from django.utils import timezone
from opencage.geocoder import OpenCageGeocode

load_dotenv()

# Function to extract the details of an event from an XML item
def extract_event_details(item):
    ns = '{events}'

    title = item.find('title').text
    link = item.find('link').text

    enclosure = item.find('enclosure')
    picture_link = enclosure.attrib['url'] if enclosure is not None else None
    
    description = item.find('description').text
    if description:
        soup = BeautifulSoup(description, 'html.parser')
        description_div = soup.find('div', class_ = 'p-description description')
        event_description = ''.join(str(content) for content in description_div.contents)
    
    categories = [category.text for category in item.findall('category')]

    pub_date = item.find('pubDate').text
    start_time = item.find(ns + 'start').text
    end_time = item.find(ns + 'end').text
    location = item.find(ns + 'location').text
    
    author = item.find('author')
    author = author.text if author is not None else None

    host = [host.text for host in item.findall(ns + 'host')]
    
    return {
        "title": title,
        "author": author,
        "pub_date": pub_date,
        "host": host,
        "link": link,
        "picture_link": picture_link,
        "event_description": event_description,
        "starttime": start_time,
        "endtime": end_time,
        "location": location,
        "categories": categories,
    }

# Get latitude and longitude using OpenCage
def get_lat_lng(location):
    geolocator = OpenCageGeocode(os.getenv("OPENCAGE_API_KEY"))

    # Append "Amherst College, Amherst, MA" to each location query
    full_location = f"{location}, Amherst College, Amherst"

    # Define bounding box around Amherst, MA
    bounding_box = [42, -73, 43, -72]

    try:
        # Pass the bounding box to restrict results
        location_obj = geolocator.geocode(full_location, bounds=bounding_box)
        if location_obj and isinstance(location_obj, list):
            location_data = location_obj[0]
            return location_data['geometry']['lat'], location_data['geometry']['lng']
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    return None, None

# Function to save the event to the Django model
def save_event_to_db(event_data):
    # Handle the `pub_date` parsing (RFC 2822 format: Thu, 31 Oct 2024 19:30:00 GMT)
    pub_date_format = '%a, %d %b %Y %H:%M:%S %Z'
    pub_date = datetime.strptime(event_data['pub_date'], pub_date_format)
    pub_date = timezone.make_aware(pub_date)

    # Handle the `start_time` and `end_time` parsing
    try:
        # First try ISO 8601 format
        iso_format = '%Y-%m-%dT%H:%M:%S'
        start_time = datetime.strptime(event_data['starttime'], iso_format)
        end_time = datetime.strptime(event_data['endtime'], iso_format)
    except ValueError:
        # If that fails, try RFC 2822 format
        rfc_format = '%a, %d %b %Y %H:%M:%S %Z'
        start_time = datetime.strptime(event_data['starttime'], rfc_format)
        end_time = datetime.strptime(event_data['endtime'], rfc_format)

    start_time = timezone.make_aware(start_time)
    end_time = timezone.make_aware(end_time)

    # The 500_000_000 (9 digits) is added to the id because hub ids (unique) are 8 digits long
    id = int(re.search(r'/(\d+)$', event_data['link']).group(1)) + 500_000_000

    # Geocode the location to get latitude and longitude
    lat, lng = get_lat_lng(event_data['location'])

    # Save the event to the database
    Event.objects.update_or_create(
        id=str(id),
        defaults={
            "id": id,
            "title": event_data['title'],
            "author_name": event_data['author_name'],
            "author_email": event_data['author_email'],
            "pub_date": pub_date,
            "host": json.dumps(event_data['host']),
            "link": event_data['link'],
            "picture_link": event_data['picture_link'],
            "event_description": event_data['event_description'],
            "start_time": start_time,
            "end_time": end_time,
            "location": event_data['location'],
            "categories": json.dumps(event_data['categories']),
            "latitude": lat if lat is not None else None,
            "longitude": lng if lng is not None else None
        }
    )

def create_events_list():
    rss_file_name = 'access_amherst_algo/rss_scraper/rss_files/hub_' + datetime.now().strftime('%Y_%m_%d_%H') + '.xml'
    root = ET.parse(rss_file_name).getroot()

    events_list = []

    # Loop through each event item and extract details
    for item in root.findall('.//item'):
        event_details = extract_event_details(item)
        events_list.append(event_details)
    
    return events_list

def save_json():
    events_list = create_events_list()

    # Save the extracted data to a JSON file as well
    output_file_name = 'access_amherst_algo/rss_scraper/json_outputs/hub_' + datetime.now().strftime('%Y_%m_%d_%H') + '.json'
    with open(output_file_name, 'w') as f:
        json.dump(events_list, f, indent=4)

def save_to_db():
    # This import is done here to avoid circular imports
    from access_amherst_algo.rss_scraper.clean_hub_data import clean_hub_data
    
    events_list = clean_hub_data()

    for event in events_list:
        save_event_to_db(event)

if __name__ == '__main__':
    save_json()
    save_to_db()