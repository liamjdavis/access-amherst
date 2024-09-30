#pip install beautifulsoup4 requests pandas

import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the webpage to scrape
url = 'https://thehub.amherst.edu/events'

# Send a GET request to fetch the raw HTML content
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find event containers 
events = soup.find_all('div', class_='engage-application')  

# Prepare lists to store event details
event_names = []
club_names = []
dates = []
times = []
locations = []

# Extract relevant information from each event card
for event in events:
    event_name = event.find('h3', class_='event-name').text.strip()  # Event Name
    club_name = event.find('div', class_='event-club').text.strip()  # Club Name
    date_time = event.find('div', class_='event-date').text.strip()  # Date and Time
    location = event.find('div', class_='event-location').text.strip()  # Location
    
    # Split date and time
    date, time = date_time.split(' at ') 
    
    # Append to lists
    event_names.append(event_name)
    club_names.append(club_name)
    dates.append(date)
    times.append(time)
    locations.append(location)

# Create a DataFrame to store the scraped data
df = pd.DataFrame({
    'Event Name': event_names,
    'Club Name': club_names,
    'Date': dates,
    'Time': times,
    'Location': locations
})

# Save the DataFrame to a CSV file
df.to_csv('events.csv', index=False)
