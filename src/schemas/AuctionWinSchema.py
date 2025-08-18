from datetime import datetime
from typing import Any, List
from pydantic import BaseModel
from src.models.AuctionSession import AuctionSession
from src.models.AuctionProduct import AuctionProduct
from src.models.AuctionResult import AuctionResult


class AuctionWinSchema(BaseModel):
    auction_info : AuctionSession
    auction_product : AuctionProduct
    auction_result : AuctionResult
