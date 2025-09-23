from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets
import logging
logger = logging.getLogger("uvicorn.error")

blocked_token_db = {}
user_db = []
session_db = {}

SECRET_KEY = "secret-key"
ALGORITHM = "HS256"

class UserId():
    id = 0
    
    @classmethod
    def get_next(cls):
        # id 1 증가 후 반환
        cls.id += 1
        return cls.id

class Password():
    ph = PasswordHasher()

    @classmethod
    def hash_password(cls, password):
        return cls.ph.hash(password) # password 단방향 암호화
    
    @classmethod
    def verify_password(cls, hashed_password, password):
        try:
            verify_result = cls.ph.verify(hashed_password, password)
        except VerifyMismatchError:
            return False
        return verify_result

class Session():
    @classmethod
    def get_session_id(cls):
        return secrets.token_hex(32) # session id 생성