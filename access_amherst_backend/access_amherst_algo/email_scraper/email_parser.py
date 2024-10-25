import imaplib
import email
from email.header import decode_header
import google.generativeai as genai
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API with API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

DEFAULT_CONFIG = {
   "temperature": 1,
   "top_p": 0.95,
   "top_k": 64,
   "max_output_tokens": 15000,
   "response_mime_type": "application/json",
}

# System instruction for extracting events and generating valid JSON format
instruction = """
    You will be provided an email containing many events. 
    Extract detailed event information and provide the result as a list of event JSON objects.
    Ensure all fields are included, even if some data is missing (set a field to "null" if the information is not present).
    Use this format for each event JSON object:

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

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=DEFAULT_CONFIG,  # Set the config to handle application/json
    system_instruction=instruction
)

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
        {email_content}
    """
    
    # Use Gemini API to generate the response
    response = model.generate_content(prompt)
    print(response.text)
    return response.text

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
            try:
                # Convert the string response to a Python object
                events_data = json.loads(extracted_events_json)

                # Generate a timestamped filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"extracted_events_{timestamp}.json"

                # get current dir
                curr_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Define the relative path to the json_outputs directory
                output_dir = os.path.join(curr_dir, "json_outputs")
                
                # Ensure the directory exists
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                # Create the full file path
                file_path = os.path.join(output_dir, filename)
                
                # Save the extracted events to a JSON file
                save_to_json_file(events_data, filename, output_dir)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
        else:
            print("No event data extracted or extraction failed.")
    else:
        print("No emails found or login failed.")