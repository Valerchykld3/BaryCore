import json
from telethon.sync import TelegramClient

with open("KEYS.json", "r", encoding="utf-8") as f:
    keys = json.load(f)

api_id = keys["api_id"]
api_hash = keys["api_hash"]

print("Client account authorization...")
with TelegramClient('user_session', api_id, api_hash) as client:
    print("Authorization successful! The file user_session.session has been created.")