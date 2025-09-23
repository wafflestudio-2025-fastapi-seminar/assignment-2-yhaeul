from fastapi import APIRouter

from src.users.router import user_router
from src.auth.router import auth_router

# 라우터 생성
api_router = APIRouter(prefix="/api") # prfix: 요청 URL에 항상 포함되어야 함

# 라우터 연결
api_router.include_router(user_router)
api_router.include_router(auth_router)