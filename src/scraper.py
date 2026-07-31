import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/scraper.log"), logging.StreamHandler()]
)

CHANNELS = [
    "CheMed",          # Replace with actual usernames
    "LobeliaCosmetics",
    "TikvahPharma"
    # Add more from et.tgstat.com/medicine
]

DATA_DIR = Path("data/raw/telegram_messages")
IMAGE_DIR = Path("data/raw/images")

async def scrape_channel(client, channel_name, days_back=30):
    """Scrape messages from a given channel and save to JSON."""
    logging.info(f"Scraping channel: {channel_name}")
    channel_entity = await client.get_entity(f"@{channel_name}")
    date_limit = datetime.now() - timedelta(days=days_back)
    
    messages = []
    async for message in client.iter_messages(channel_entity, offset_date=date_limit, reverse=True):
        msg_data = {
            "message_id": message.id,
            "channel_name": channel_name,
            "message_date": message.date.isoformat(),
            "message_text": message.text or "",
            "has_media": bool(message.media),
            "views": message.views or 0,
            "forwards": message.forwards or 0,
            "image_path": None
        }
        # Download image if present
        if message.media and isinstance(message.media, MessageMediaPhoto):
            img_dir = IMAGE_DIR / channel_name
            img_dir.mkdir(parents=True, exist_ok=True)
            img_path = img_dir / f"{message.id}.jpg"
            await client.download_media(message.media, file=img_path)
            msg_data["image_path"] = str(img_path)
        
        messages.append(msg_data)
    
    # Save to JSON partitioned by date
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = DATA_DIR / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{channel_name}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    logging.info(f"Saved {len(messages)} messages for {channel_name} to {out_file}")

async def main():
    async with TelegramClient("session", API_ID, API_HASH) as client:
        await client.start(phone=PHONE)
        for channel in CHANNELS:
            try:
                await scrape_channel(client, channel)
            except Exception as e:
                logging.error(f"Error scraping {channel}: {e}")

if name == "main":
    asyncio.run(main())
