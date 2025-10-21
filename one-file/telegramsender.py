import os

import requests
import json
from dotenv import load_dotenv

load_dotenv()
KEY = str(os.getenv('KEY'))
TODAY_CHAT_ID = str(os.getenv('TODAY_CHAT_ID'))
UPCOMING_CHAT_ID = str(os.getenv('UPCOMING_CHAT_ID'))
DAMIENS_CHAT_ID = str(os.getenv('DAMIENS_CHAT_ID'))

def send_data_to_telegram():
    json_file = 'Events.json'

    # Load JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for event in data:
        title = event['Title'] or ""
        date = event['Date'] or ""
        desc = event['Description'] or ""
        link = event['Link'] or ""

        # check if date is today if so send to today channel
        message = (title + "\n" if title else "") + \
                  (f"📅 Date: {date}\n" if date else "") + \
                  (f"📜 Description: {desc}\n" if desc else "") + \
                  (f"⛓️‍💥 Link: {link}\n" if link else "") \

        send_message(message, UPCOMING_CHAT_ID)

def send_message(message, channel_id):
    requests.post(f'https://api.telegram.org/bot{KEY}/sendMessage?chat_id={channel_id}&text=%s' % message)
    print("Sent message: " + message)
    print("CHANNEL_ID: " + channel_id)

    # Check the date here
    # print(dates)
    #print("Datum:", dates[0])
    #print("Titel:",titles[0])
    #print("Link:",links[0])


send_data_to_telegram()