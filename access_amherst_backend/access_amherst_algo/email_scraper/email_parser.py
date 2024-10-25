import imaplib
import email
from email.header import decode_header
import google.generativeai as genai
import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API with API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Replace with your Gemini API key

# Function to connect to Gmail and fetch the latest email from a specific sender
def connect_and_fetch_latest_email(app_password, subject_filter, mail_server="imap.gmail.com"):
    mail = imaplib.IMAP4_SSL(mail_server)
    try:
        mail.login(os.getenv("EMAIL_ADDRESS"), app_password)
        print("Logged in successfully")
    except imaplib.IMAP4.error as e:
        print(f"Login failed: {e}")
        return None

    mail.select("inbox")
    status, messages = mail.search(None, f'SUBJECT "{subject_filter}"')
    if status != "OK":
        print(f"Failed to fetch emails: {status}")
        return None

    for msg_num in messages[0].split()[-1:]:  # Only fetch the latest message
        res, msg = mail.fetch(msg_num, "(RFC822)")
        for response_part in msg:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                return msg
    return None

# Function to extract the email body
def extract_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                return part.get_payload(decode=True).decode('utf-8')
    else:
        return msg.get_payload(decode=True).decode('utf-8')

# Function to send email content to Gemini API and get JSON response
def extract_event_info_using_gemini(email_content):
    prompt = f"""
        Extract detailed event information from the following email content and provide the result in valid JSON format. 

        Email content:
        {email_content}

        Follow these guidelines:

        1. Ensure all fields are included, even if some data is missing (use empty strings if necessary).
        2. Format the result as a valid JSON object without missing quotations or delimiters.
        3. Validate the JSON before returning it.
        4. Use this format for each event:

        {{
            "title": "Event Title",
            "pub_date": "YYYY-MM-DD",
            "starttime": "HH:MM:SS",
            "endtime": "HH:MM:SS",
            "location": "Event Location",
            "event_description": "Event Description",
            "host": ["Host Organization"],
            "link": "Event URL",
            "picture_link": "Image URL",
            "categories": ["Category 1", "Category 2"],
            "author_name": "Author Name",
            "author_email": "author@email.com"
        }}

        Ensure all fields follow the exact format above.
    """
    
    # Use Gemini API to generate the response
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    if response.candidates[0].content.parts[0].text:
        return response.candidates[0].content.parts[0].text
    else:
        return None

def save_to_json_file(data, filename, folder):
    # Ensure the folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Construct the full file path
    file_path = os.path.join(folder, filename)

    try:
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)  # Save data with indentation for readability
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"Failed to save data to {file_path}: {e}")

def parse_email(subject_filter):
    app_password = os.getenv("EMAIL_PASSWORD")
    subject_filter = subject_filter

    msg = connect_and_fetch_latest_email(app_password, subject_filter)
    if msg:
        email_body = extract_email_body(msg)
        print("Email fetched successfully.")
        
        extracted_events_json = extract_event_info_using_gemini(email_body)
        
        if extracted_events_json:  # Ensure data exists
            # Generate a timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"extracted_events_{timestamp}.json"
            
            # Save the extracted_events_json to a file in the json_outputs folder
            save_to_json_file(extracted_events_json, filename, "json_outputs")
        else:
            print("No event data extracted or extraction failed.")
    else:
        print("No emails found or login failed.")