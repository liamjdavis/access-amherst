import json
from datetime import datetime
from parse_rss import create_events_list, save_to_db

def clean_hub_data(events_list=None):
    if events_list is None:
        events_list = create_events_list()
    
    cleaned_events = []
    for event in events_list:
        # Remove cancelled events
        if "Cancelled" in event['title']:
            continue

        # Split author into name and email
        if event['author'] is not None:
            author_email, author_name = event['author'].split(" (", 1)
            author_name = author_name.rstrip(")")
            event['author_name'] = author_name
            event['author_email'] = author_email
            del event['author']

        cleaned_events.append(event)
    
    # Save cleaned events to the database
    save_to_db(cleaned_events)

    # Save the extracted data to a JSON file as well
    output_file_name = 'access_amherst_algo/rss_scraper/cleaned_json_outputs/hub_' + datetime.now().strftime('%Y_%m_%d_%H') + '.json'
    with open(output_file_name, 'w') as f:
        json.dump(events_list, f, indent=4)
