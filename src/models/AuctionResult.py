from beanie import Document
from pydantic import Field, field_validator
from decimal import Decimal
from bson.decimal128 import Decimal128


class AuctionResult(Document):
    auction_id: str
    product_id: str
    quantity: int
    bidder_id: str
    hoster_id: str
    bidder_amount: Decimal
    host_claim_amount: Decimal
    is_solved: bool

    @field_validator("bidder_amount", mode="before")
    @classmethod
    def convert_bidder_amount(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v

    @field_validator("host_claim_amount", mode="before")
    @classmethod
    def convert_host_claim_amount(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v

    class Settings:
        name = "AuctionResult"
