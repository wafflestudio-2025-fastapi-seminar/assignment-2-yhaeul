from fastapi import APIRouter, Depends, Cookie, status, Response, Request, Header

from src.common.database import blocked_token_db, session_db, user_db, Session, Password, SECRET_KEY, ALGORITHM
from src.auth.schemas import UserLoginRequest, UserToken
from src.users.errors import *

from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

import logging
logger = logging.getLogger('uvicorn.error')

auth_router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SHORT_SESSION_LIFESPAN = 15
LONG_SESSION_LIFESPAN = 24 * 60

def authenticate_user(request: UserLoginRequest):
    for user in user_db:
        if request.email == user["email"]:
            if Password.verify_password(user["hashed_password"], request.password):
                return user["email"]
            else:
                raise InvalidAccountException()
    raise InvalidAccountException()

def create_token(sub: str, expires_delta: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    claim = {"sub": sub, "exp": expire}
    encoded_jwt = jwt.encode(claim, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@auth_router.post("/token", status_code=status.HTTP_200_OK)
def token_login(user_email: str= Depends(authenticate_user)) -> UserToken:
    access_token = create_token(sub=user_email, expires_delta=SHORT_SESSION_LIFESPAN)
    refresh_token = create_token(sub=user_email, expires_delta=LONG_SESSION_LIFESPAN)
    return UserToken(
        access_token=access_token,
        refresh_token=refresh_token
    )

@auth_router.post("/token/refresh", status_code=status.HTTP_200_OK)
def update_token(authorization: str = Header(default=None)) -> UserToken:
    try:
        token_type, old_refresh_token = authorization.split(" ") 
    except Exception:
        raise BadAuthorizationHeaderException()
    if token_type != "Bearer":
        raise BadAuthorizationHeaderException()
    if old_refresh_token in blocked_token_db:
        raise InvalidTokenException()
    
    try:
        payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM]) # 위조, 변조, 만료 확인 포함
        user_email = payload.get("sub")
    except JWTError:
        raise InvalidTokenException()
    
    access_token = create_token(sub=user_email, expires_delta=SHORT_SESSION_LIFESPAN)
    refresh_token = create_token(sub=user_email, expires_delta=LONG_SESSION_LIFESPAN)

    blocked_token_db[old_refresh_token] = payload.get("exp")

    return UserToken(
        access_token=access_token,
        refresh_token=refresh_token
    )

@auth_router.delete("/token", status_code=status.HTTP_204_NO_CONTENT)
def delete_token(authorization: str = Header(default=None)) -> Response:
    try:
        token_type, refresh_token = authorization.split(" ") 
    except Exception:
        raise BadAuthorizationHeaderException()
    if token_type != "Bearer":
        raise BadAuthorizationHeaderException()
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM]) # 위조, 변조, 만료 확인 포함
    except JWTError:
        raise InvalidTokenException()
    
    blocked_token_db[refresh_token] = payload.get("exp")
    
    return Response()

@auth_router.post("/session", status_code=status.HTTP_200_OK)
def session_login(response: Response, user_email: str= Depends(authenticate_user)):
    sid = Session.get_session_id()
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=LONG_SESSION_LIFESPAN)
    session_db[sid] = {"user_email": user_email, "expire_at": expire_at}
    response.set_cookie(
        key="sid",
        value=sid,
        httponly=True,
        max_age=LONG_SESSION_LIFESPAN * 60,
    )
    return {"message": "login"}
        
@auth_router.delete("/session", status_code=status.HTTP_204_NO_CONTENT)
def session_logout(request: Request, response: Response) -> Response: # Request를 통해 요청의 쿠키 접근
    sid = request.cookies.get("sid")
    if sid:
        response.delete_cookie(key="sid") # 클라이언트의 쿠키 만료
        if sid in session_db.keys(): # 서버에 저장된 세션이 존재한다면 제거
            session_db.pop(sid, None)