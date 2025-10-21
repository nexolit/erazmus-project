import os

import requests
import json
from dotenv import load_dotenv

load_dotenv()
KEY = str(os.getenv('KEY'))
CHAT_ID = str(os.getenv('CHAT_ID'))

def send_data_to_telegram():
    json_file = 'Goabase.json'

    # Load JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for event in data:
        message = ""
        for item, value in event.items():
            message += item + ": " + value + "\n"

        requests.post(f'https://api.telegram.org/bot{KEY}/sendMessage?chat_id={CHAT_ID}&text=%s' % message)

    # print(dates)
    #print("Datum:", dates[0])
    #print("Titel:",titles[0])
    #print("Link:",links[0])


send_data_to_telegram()