import os

import requests
import json
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
KEY = str(os.getenv('KEY'))
TODAY_CHAT_ID = str(os.getenv('TODAY_CHAT_ID'))
UPCOMING_CHAT_ID = str(os.getenv('UPCOMING_CHAT_ID'))

# Convert JSON Lines to standard JSON
def open_jsonlines(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        items = [json.loads(line) for line in f]
        return items

def clean_str(string):
    return re.sub('[^A-Za-z0-9 :/._-]+', '', string).strip()

def send_data_to_telegram():
    json_file = 'Events.jsonl'

    # Load JSON file
    data = open_jsonlines(json_file)

    for event in data:
        title = clean_str(event['Title']) or ""
        date = clean_str(event['Date']) or ""
        desc = clean_str(event['Description']) or ""
        link = clean_str(event['Link']) or ""

        message = (title + "\n" if title else "") + \
                  (f"📅 Date: {date}\n" if date else "") + \
                  (f"📜 Description: {desc}\n" if desc else "") + \
                  (f"⛓️‍💥 Link: {link}\n" if link else "") \

        # check if date is today if so send to today channel
        if datetime.today().strftime("%d.%m.%Y") == date:
            send_message(message, TODAY_CHAT_ID)
        else:
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