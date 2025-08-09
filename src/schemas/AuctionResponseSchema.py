from datetime import datetime
from typing import Any, List
from pydantic import BaseModel


class AuctionResponseSchema(BaseModel):
    host_username : str
    auction_id : str
    start_time : datetime
    end_time : datetime
    product_id : str
    quantity : int
    status : int

