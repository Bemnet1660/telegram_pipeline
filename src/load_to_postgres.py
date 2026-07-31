import json
import psycopg2
from pathlib import Path
from datetime import datetime

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="telegram_warehouse",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

# Create raw schema and table
cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
cur.execute("""
CREATE TABLE IF NOT EXISTS raw.telegram_messages (
    message_id BIGINT,
    channel_name TEXT,
    message_date TIMESTAMP,
    message_text TEXT,
    has_media BOOLEAN,
    views INT,
    forwards INT,
    image_path TEXT,
    raw_json JSONB
);
""")

# Load all JSON files
data_dir = Path("data/raw/telegram_messages")
for json_path in data_dir.glob("**/*.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        messages = json.load(f)
    for msg in messages:
        cur.execute("""
            INSERT INTO raw.telegram_messages 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            msg["message_id"], msg["channel_name"], msg["message_date"],
            msg["message_text"], msg["has_media"], msg["views"],
            msg["forwards"], msg["image_path"], json.dumps(msg)
        ))
conn.commit()
cur.close()
conn.close()
print("Data loaded successfully.")
