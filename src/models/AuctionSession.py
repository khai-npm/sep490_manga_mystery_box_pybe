from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class AuctionSession(Document):
    title : str
    descripition : str
    start_time : datetime
    end_time : datetime
    seller_id : str
    status : int



    class Settings:
        name = "AuctionSession"