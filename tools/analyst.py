import json
import os
import re
import threading
import asyncio
from telethon import TelegramClient 

# Tools for DNIB

CACHE_FILE = "channels_cache.json"
telethon_lock = threading.Lock()

async def get_entity_from_cache(client: TelegramClient, channel_name: str):
    def normalize(text: str) -> str:
        return re.sub(r'[\s\W_]+', '', text.lower())

    search_target = normalize(channel_name)
    cache = {}
    
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
            
    for name, entity_id in cache.items():
        if search_target in normalize(name):
            return entity_id
            
    print("Channel not found in cache. Updating the list of conversations...")
    cache = {}
    
    async for dialog in client.iter_dialogs(limit=500):
        if dialog.is_channel or dialog.is_group:
            cache[dialog.name] = dialog.id
            
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)
        
    for name, entity_id in cache.items():
        if search_target in normalize(name):
            return entity_id
            
    return None

def get_channel_history(channel_name: str, limit: int = 20) -> str:
    print(f"Gathering news from the channel {channel_name}...")
    safe_limit = min(limit, 15)
    
    try:
        with open("KEYS.json", "r", encoding="utf-8") as f:
            keys = json.load(f)
        api_id = int(keys.get("api_id"))
        api_hash = keys.get("api_hash")
        
        if not api_id or not api_hash:
            return "An error: api_id and api_hash was not found in KEYS.json."
    except Exception as e:
        return f"Error reading KEYS.json: {str(e)}"

    async def _fetch_history():
        client = TelegramClient('user_session', api_id, api_hash)
        await client.connect()
        
        try:
            target_entity = None
            
            if channel_name.startswith('@') or 't.me/' in channel_name:
                target_entity = channel_name
            else:
                target_entity = await get_entity_from_cache(client, channel_name)
            
            if not target_entity:
                return f"Error: Channel '{channel_name}' not found among subscriptions. Ask the user to provide the exact @username."

            messages = await client.get_messages(target_entity, limit=safe_limit)
            
            if not messages:
                return f"No messages found, or access to {channel_name} is denied."
            
            result = f"Latest {len(messages)} posts from {channel_name}:\n\n"
            for msg in messages:
                date_str = msg.date.strftime('%Y-%m-%d %H:%M') if msg.date else "Unknown date"
                text = msg.text if msg.text else "[Media file without text]"
                result += f"[{date_str}]\n{text}\n{'='*40}\n"
            
            return result
        finally:
            await client.disconnect() 

    try:
        with telethon_lock:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(_fetch_history())
    except Exception as e:
        return f"Error retrieving channel history: {str(e)}"