from typing import Any, List
from pydantic import BaseModel


class BodyResponseSchema(BaseModel):
    success: bool = True
    data: List[Any] = []
    length: int = 0
    error: str = ""
    error_code: int = 0


