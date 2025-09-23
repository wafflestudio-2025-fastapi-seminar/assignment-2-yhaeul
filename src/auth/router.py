from fastapi import APIRouter, Depends, Cookie, status, Response, Request

from src.common.database import blocked_token_db, session_db, user_db, Session, Password
from src.auth.schemas import UserLoginRequest
from src.users.errors import InvalidAccountException

import logging
logger = logging.getLogger('uvicorn.error')

auth_router = APIRouter(prefix="/auth", tags=["auth"])

SHORT_SESSION_LIFESPAN = 15
LONG_SESSION_LIFESPAN = 24 * 60

# @auth_router.post("/token")


# @auth_router.post("/token/refresh")


# @auth_router.delete("/token")


@auth_router.post("/session", status_code=status.HTTP_200_OK)
def session_login(request: UserLoginRequest, response: Response) -> Response:
    for user in user_db:
        if request.email == user["email"]:
            if not Password.verify_password(user["hashed_password"], request.password):
                raise InvalidAccountException()
            sid = Session.get_session_id()
            session_db[sid] = user["user_id"]
            response.set_cookie(
                key="sid",
                value=sid,
                httponly=True,
                max_age=LONG_SESSION_LIFESPAN * 60,
            )
            return Response()
    raise InvalidAccountException()
        
@auth_router.delete("/session", status_code=status.HTTP_204_NO_CONTENT)
def session_logout(request: Request, response: Response) -> Response: # Request를 통해 요청의 쿠키 접근
    sid = request.cookies.get("sid")
    if sid:
        response.delete_cookie(key="sid") # 클라이언트의 쿠키 만료
        if sid in session_db.keys(): # 서버에 저장된 세션이 존재한다면 제거
            session_db.pop(sid, None)