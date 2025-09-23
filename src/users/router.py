from typing import Annotated
from argon2 import PasswordHasher

from fastapi import (
    APIRouter,
    Depends,
    Cookie,
    Header,
    status
)

from src.users.schemas import CreateUserRequest, UserResponse
from src.common.database import blocked_token_db, session_db, user_db, UserId


# 라우터 생성
user_router = APIRouter(prefix="/users", tags=["users"])

ph = PasswordHasher()

@user_router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(request: CreateUserRequest) -> UserResponse:
    user_id = UserId.get_next()
    hashed_password = ph.hash(request.password) # password 단방향 암호화

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

@user_router.get("/me")
def get_user_info():
    pass