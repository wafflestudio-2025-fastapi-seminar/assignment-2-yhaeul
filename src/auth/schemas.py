from pydantic import BaseModel, EmailStr

class UserLoginRequest(BaseModel): 
    email: EmailStr
    password: str

class UserToken(BaseModel):
    access_token: str
    refresh_token: str
