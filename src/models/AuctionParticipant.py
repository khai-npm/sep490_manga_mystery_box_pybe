from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class AuctionParticipant(Document):
    auction_id : str
    user_id : str
    class Settings:
        name = "AuctionParticipant"