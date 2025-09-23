import re

from pydantic import BaseModel, field_validator, EmailStr
from fastapi import HTTPException

from src.users.errors import *
from src.common.database import user_db

class CreateUserRequest(BaseModel): 
    name: str
    email: EmailStr
    password: str
    phone_number: str
    bio: str | None = None
    height: float

    @field_validator('password', mode='after') # 검증하려는 필드
    def validate_password(cls, v): # v: 검증하려는 필드 값
        if len(v) < 8 or len(v) > 20:
            raise InvalidPasswordException()
        return v # 필드 값을 그대로 리턴하지 않으면 None으로 덮임
    
    @field_validator('phone_number', mode='after')
    def validate_phone_number(cls, v):
        if not re.match(r"^010-\d{4}-\d{4}$", v):
            raise InvalidPhoneNumberException()
        return v

    @field_validator('bio', mode='after')
    def validate_bio(cls, v):
        if len(v) > 500:
            raise InvalidBioLengthException()
        return v
    
    @field_validator('email', mode='after')
    def validate_email(cls, v):
        email_list = [user.get("email") for user in user_db]
        if v in email_list:
            raise DuplicateEmailException()
        return v

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone_number: str
    bio: str | None = None
    height: float