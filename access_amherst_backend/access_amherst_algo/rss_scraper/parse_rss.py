import xml.etree.ElementTree as ET
import json
from datetime import datetime

# Function to extract the details of an event from an XML item
def extract_event_details(item):
    # Special namespace for the start, end, location, status, and host tags
    ns = '{events}'

    title = item.find('title').text
    link = item.find('link').text

    # When an event is posted to the hub, a picture is not required;
    # if a picture is not included, the tag corresponding to the image does not exist,
    # and the hub will display a placeholder image.
    enclosure = item.find('enclosure')
    picture_link = enclosure.attrib['url'] if enclosure is not None else None
    
    # Extract event description from the description CDATA
    description = item.find('description').text
    if description:
        description_start = description.find('<div class="p-description description">') + len('<div class="p-description description">')
        description_end = description.find('</div>', description_start)
        event_description = description[description_start:description_end]
        
    
    categories = [category.text for category in item.findall('category')]

    pub_date = item.find('pubDate').text

    start_time = item.find(ns + 'start').text
    end_time = item.find(ns + 'end').text
    
    location = item.find(ns + 'location').text
    
    # Some events do not have an author
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

# Parse the XML
rss_file_name = 'access_amherst_backend/access_amherst_algo/rss_scraper/rss_files/hub_' + datetime.now().strftime('%Y_%m_%d_%H') + '.xml'
root = ET.parse(rss_file_name).getroot()

# List to store extracted event data
events_list = []

# Loop through each event item and extract details
for item in root.findall('.//item'):
    event_details = extract_event_details(item)
    events_list.append(event_details)

output_file_name = 'access_amherst_backend/access_amherst_algo/rss_scraper/json_outputs/hub_' + datetime.now().strftime('%Y_%m_%d_%H') + '.json'
with open(output_file_name, 'w') as f:
    json.dump(events_list, f, indent=4)
