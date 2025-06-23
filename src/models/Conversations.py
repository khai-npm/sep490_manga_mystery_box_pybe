from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class Conversations(Document):
    participant_1 : str
    participant_2 : str
    created_by : str
    created_at : datetime  

    class Settings:
        name = "Conversations"