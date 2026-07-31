from pydantic import BaseModel
from typing import List, Optional

class Product(BaseModel):
    term: str
    count: int

class ChannelActivity(BaseModel):
    date: str
    post_count: int
    avg_views: float

class Message(BaseModel):
    message_id: int
    channel: str
    text: str
    views: int

class VisualStats(BaseModel):
    channel: str
    total_images: int
    promotional: int
    product_display: int
    lifestyle: int
