from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class AuctionWinner(Document):
    auction_id : str
    winner_id : str
    bid_amount : float
    winning_time : datetime  

    class Settings:
        name = "AuctionWinner"