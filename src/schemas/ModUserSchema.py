from pydantic import BaseModel

class ModUserSchema(BaseModel):
    id : str
    username : str
    role_id : str