from pydantic import BaseModel

class PasswordRecoverySchema(BaseModel):
    email : str
    code : str
    password : str
