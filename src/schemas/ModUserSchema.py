from pydantic import BaseModel, Field, BeforeValidator
from typing import Annotated

ObjectIdStr = Annotated[str, BeforeValidator(lambda v: str(v))]

class ModUserSchema(BaseModel):
    id: ObjectIdStr = Field(alias="_id")
    username: str
    role_id: str
    is_active : bool

    class Config:
        populate_by_name = True
