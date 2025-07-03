from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class Bids(Document):
    auction_id : str
    bidder_id : str
    bid_amount : float
    bid_time : datetime




    class Settings:
        name = "Bids"