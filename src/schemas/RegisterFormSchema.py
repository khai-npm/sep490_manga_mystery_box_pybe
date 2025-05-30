from pydantic import BaseModel

class RegisterFormSchema(BaseModel):
    email : str
    username : str
    password : str
