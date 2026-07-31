from fastapi import FastAPI, Query, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from .schemas import Product, ChannelActivity, Message, VisualStats

app = FastAPI()

conn_params = {
    "host": "localhost",
    "port": 5432,
    "database": "telegram_warehouse",
    "user": "postgres",
    "password": "postgres"
}

def get_db():
    return psycopg2.connect(**conn_params, cursor_factory=RealDictCursor)

@app.get("/api/reports/top-products")
def top_products(limit: int = Query(10, ge=1, le=100)):
    """Returns most frequently mentioned terms (simple word count)."""
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT word, COUNT(*) as count
            FROM (
                SELECT regexp_split_to_table(lower(message_text), '\s+') as word
                FROM fct_messages
            ) t
            WHERE length(word) > 3
            GROUP BY word
            ORDER BY count DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()

@app.get("/api/channels/{channel_name}/activity")
def channel_activity(channel_name: str):
    """Returns daily posting activity for a channel."""
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT d.full_date, COUNT(f.message_id) as post_count, AVG(f.views) as avg_views
            FROM fct_messages f
            JOIN dim_channels c ON f.channel_key = c.channel_key
            JOIN dim_dates d ON f.date_key = d.date_key
            WHERE c.channel_name = %s
            GROUP BY d.full_date
            ORDER BY d.full_date
        """, (channel_name,))
        return cur.fetchall()

@app.get("/api/search/messages")
def search_messages(query: str = Query(..., min_length=1), limit: int = 20):
    """Search for messages containing a keyword."""
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT f.message_id, c.channel_name, f.message_text, f.views
            FROM fct_messages f
            JOIN dim_channels c ON f.channel_key = c.channel_key
            WHERE f.message_text ILIKE %s
            ORDER BY f.views DESC
            LIMIT %s
        """, (f"%{query}%", limit))
        return cur.fetchall()

@app.get("/api/reports/visual-content")
def visual_content():
    """Returns visual content statistics per channel."""
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT c.channel_name,
                   COUNT(f.message_id) as total_images,
                   SUM(CASE WHEN d.category = 'promotional' THEN 1 ELSE 0 END) as promotional,
                   SUM(CASE WHEN d.category = 'product_display' THEN 1 ELSE 0 END) as product_display,
                   SUM(CASE WHEN d.category = 'lifestyle' THEN 1 ELSE 0 END) as lifestyle
            FROM fct_messages f
            JOIN dim_channels c ON f.channel_key = c.channel_key
            LEFT JOIN fct_image_detections d ON f.message_id = d.message_id
            WHERE f.has_image = true
            GROUP BY c.channel_name
        """)
        return cur.fetchall()
