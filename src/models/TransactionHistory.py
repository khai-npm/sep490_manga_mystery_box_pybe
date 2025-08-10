from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class TransactionHistory(Document):
    WalletId : str
    DataTime : datetime
    Type : int
    Status : int
    Amount : int
    TransactionCode : str


    class Settings:
        name = "TransactionHistory"