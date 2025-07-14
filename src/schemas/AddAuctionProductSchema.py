from typing import Any, List
from pydantic import BaseModel


class AddAuctionProductSchema(BaseModel):
    product_id : str
    quantity : int
    starting_price : float
