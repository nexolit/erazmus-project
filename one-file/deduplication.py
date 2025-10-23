import requests
import time
import json
import os

BOT_TOKEN = "YOUR_BOT_TOKEN"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# File to persist seen messages
SEEN_FILE = "seen_messages.json"
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        seen_messages = set(json.load(f))
else:
    seen_messages = set()

LAST_UPDATE_ID = None

def get_updates():
    global LAST_UPDATE_ID
    params = {"timeout": 100}  # long polling
    if LAST_UPDATE_ID is not None:
        params["offset"] = LAST_UPDATE_ID + 1

    r = requests.get(f"{BASE_URL}/getUpdates", params=params)
    data = r.json()
    if data["ok"]:
        return data["result"]
    return []

def delete_message(chat_id, message_id):
    requests.get(f"{BASE_URL}/deleteMessage", params={"chat_id": chat_id, "message_id": message_id})

def save_seen_messages():
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_messages), f, ensure_ascii=False, indent=2)

def deduplicate():
    global LAST_UPDATE_ID
    updates = get_updates()

    for update in updates:
        LAST_UPDATE_ID = update["update_id"]

        if "message" in update:
            msg = update["message"]
            text = msg.get("text")
            chat_id = msg["chat"]["id"]
            message_id = msg["message_id"]

            if text is None:
                continue  # skip non-text messages

            # Check if the message was sent by the bot itself
            from_id = msg.get("from", {}).get("id")

            if text in seen_messages:
                print(f"Duplicate found, deleting: {text}")
                delete_message(chat_id, message_id)
            else:
                # Only mark as seen if it’s a bot message or new user message
                seen_messages.add(text)
                print(f"New message: {text}")

    save_seen_messages()

if __name__ == "__main__":
    while True:
        try:
            deduplicate()
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
