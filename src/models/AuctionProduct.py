from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class AuctionProduct(Document):
    auction_session_id : str
    user_product_id : str
    seller_id : str
    quantity : int
    starting_price : float
    status : int

    class Settings:
        name = "AuctionProduct"