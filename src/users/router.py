from typing import Annotated
from datetime import datetime, timezone
from jose import JWTError, jwt

from fastapi import (
    APIRouter,
    Depends,
    Cookie,
    Header,
    status,
)

from src.users.schemas import CreateUserRequest, UserResponse
from src.common.database import blocked_token_db, session_db, user_db, UserId, Password, SECRET_KEY, ALGORITHM
from src.users.errors import *

import logging
logger = logging.getLogger('uvicorn.error')

# 라우터 생성
user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(request: CreateUserRequest) -> UserResponse:
    email_list = [user.get("email") for user in user_db]
    if request.email in email_list:
        raise DuplicateEmailException()
    user_id = UserId.get_next()
    hashed_password = Password.hash_password(request.password) # password 단방향 암호화

    user_dict = {"user_id": user_id, "hashed_password": hashed_password}
    user_data = request.model_dump() # pydantic 모델을 딕셔너리로 변환
    del(user_data["password"]) # 평문 password 삭제
    user_dict.update(user_data)
    
    user_db.append(user_dict)

    return UserResponse(
        user_id=user_id,
        email=request.email,
        name=request.name,
        phone_number=request.phone_number,
        height=request.height,
        bio=request.bio
    )

@user_router.get("/me", status_code=status.HTTP_200_OK)
def get_user_info(sid: str = Cookie(default=None), authorization: str = Header(default=None)) -> UserResponse:
    if sid:
        session = session_db.get(sid)
        if sid not in session_db:
            raise InvalidSessionException()
        elif session.get("expire_at") < datetime.now(timezone.utc):
            raise InvalidSessionException()
        
        user_email = session.get("user_email")

        for user in user_db:
            if user["email"] == user_email:
                user_copy = user.copy()
                user_copy.pop("hashed_password")
                return UserResponse(**user_copy)

    elif authorization:
        try:
            token_type, access_token = authorization.split(" ") 
        except Exception:
            raise BadAuthorizationHeaderException()
        if token_type != "Bearer":
            raise BadAuthorizationHeaderException()
        
        try:
            decoded_access_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM]) # 위조, 변조, 만료 확인 포함
            user_email = decoded_access_token.get("sub")     
        except JWTError:
            raise InvalidTokenException()

        for user in user_db:
            if user["email"] == user_email:
                user.pop("hashed_password")
                return UserResponse(**user)   

    raise UnauthenticatedException()

    