from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from src.api import api_router
from src.common.custom_exception import CustomException
from src.users.errors import *

from tests.util import get_all_src_py_files_hash

app = FastAPI()

app.include_router(api_router) # 라우터 연결

# 요청이 invalid data를 포함할 때, FastAPI는 RequestValidationError를 발생
@app.exception_handler(RequestValidationError) # default exception_handler를 override
def handle_request_validation_error(request, exc: RequestValidationError) -> JSONResponse:
    if any(err["msg"] == "Field required" for err in exc.errors()):
        raise MissingValueException()
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()} # 상세 설명 반환
    )

# CustomException에 대한 exception_handler
@app.exception_handler(CustomException)
def handle_custom_exception(request, exc: CustomException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
 	        "error_msg": exc.error_message
        }
    )

@app.get("/health")
def health_check():
    # 서버 정상 배포 여부를 확인하기 위한 엔드포인트입니다.
    # 본 코드는 수정하지 말아주세요!
    hash = get_all_src_py_files_hash()
    return {
        "status": "ok",
        "hash": hash
    }