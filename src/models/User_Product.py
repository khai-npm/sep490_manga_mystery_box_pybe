from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class User_Product(Document):
    CollectionId : str
    ProductId : str
    Quantity : int
    CollectedAt : datetime
    CollectorId : str
    class Settings:
        name = "User_Product"