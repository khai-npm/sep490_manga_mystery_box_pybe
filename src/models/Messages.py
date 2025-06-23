from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class Messages(Document):
    conversation_id : str
    sender_id : str
    content : str
    created_at : datetime

    class Settings:
        name = "Messages"