import pandas as pd

events_data = {
    "Event Name": [
        "Academic Kaffeeklatsch", "CHEMINAR - Senior Thesis Talks (Week 2 of 5)",
        "Physics & Astronomy Colloquium: Aurelia Ball", "Extended Course Reserve Loans", 
        "T4Tea", "CHI Salon - Repairing History", "Science Center A Wing Paint Work", 
        "Webster Hall Window Inspections", "College Hall Driveway Paving", 
        "Prof. Jason Robinson Performs Ancestral Numbers at The Drake", 
        "I came here to weep: A conversation with the artist Yanira Castro", 
        "La Mesa del Español", "Media Influence and Consumer Literacy | Five College Election Panel Series", 
        "Queer Talk", "Baewatch: Beauty Standards at Amherst", 
        "Pulse & Breath: A Weekly Moment to Honor What We Are Living Through", 
        "Amherst's first outdoor Pride festival", "BREHA Lab: Theatre as a Tool for Political Engagement & Community Collaboration", 
        "Exorcism = Liberation hub at Book & Plow", "Peer Educator Applications", 
        "Fall Break Wellness & Fitness Classes", "Naloxone Training", 
        "Admission Office Blogger Applications", "Amherst College Event Calendar"
    ],
    "Event Date": [
        "Friday, October 11, 2024", "Friday, October 11, 2024", "October 8, 2024",
        "Starting Friday, October 11th", "October 17th", "10/16", "10/14/2024-10/18/2024",
        "Monday, October 14, 2024", "10/15/2024-10/18/2024", "Thursday, October 17",
        "Thursday, October 17", "Fridays", "Monday, October 14", "No Queer Talk on October 11th",
        "Friday, October 11th", "Fridays", "April 2025", "October 16 at 5:30 p.m. & October 17 at 4:30 p.m.",
        "Ongoing", "Applications due by Wednesday October 16th @ 11:59pm", "Monday 10/14 - Tuesday 10/15", 
        "Thursday, Oct. 17", "Applications open until October 11 at 5 PM", "Ongoing"
    ],
    "Event Time": [
        "3pm", "Not specified", "4:00 PM-5:00 PM", "Not specified", "6:30pm - 8:00pm", "4:30pm", 
        "Not specified", "Not specified", "Not specified", "7:30 PM", "4:30 PM", "12-2pm", "6pm", 
        "Not applicable", "12:30 PM - 2:00 PM", "4:00 PM - 4:45 PM", "Not specified", 
        "Not specified", "Not specified", "Various", "12:00 PM - 1:00 PM", "Not specified", "Ongoing"
    ],
    "Event Location": [
        "Porter House", "Science Center A011, Kirkpatrick Lecture Hall", 
        "Science Center, A011", "Frost, Music, and Science Reserves", "WGC", 
        "CHI Think Tank (Childcare provided in Lyceum 102)", "Science Center A Wing", 
        "Webster Hall", "Driveway behind College Hall", "The Drake", 
        "Friendly Reading Room, Frost Library (1st floor)", "Valentine Hall (2nd floor)", 
        "Virtual (Zoom)", "Not applicable", "QRC", "Religious & Spiritual Life, Keefe Campus Center #017", 
        "Not specified", "Cole Assembly Room in Converse Hall (10/16), Webster 220 (10/17)", 
        "Book & Plow", "Workday (JR-5522)", "Various", "Val Terrace Room", 
        "Workday", "Not specified"
    ]
}

# Create DataFrame
events_df = pd.DataFrame(events_data)

# Display DataFrame
print(events_df)
