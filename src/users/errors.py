from src.common import CustomException
from fastapi import status

class MissingValueException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="ERR_001",
            error_message="MISSING VALUE"
        )

class InvalidPasswordException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="ERR_002",
            error_message="INVALID PASSWORD"
        )

class InvalidPhoneNumberException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="ERR_003",
            error_message="INVALID PHONE NUMBER"
        )

class InvalidBioLengthException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="ERR_004",
            error_message="BIO TOO LONG"
        )

class DuplicateEmailException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="ERR_005",
            error_message="EMAIL ALREADY EXISTS"
        )

class InvalidSessionException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="ERR_006",
            error_message="INVALID SESSION"
        )

class BadAuthorizationHeaderException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="ERR_007",
            error_message="BAD AUTHORIZATION HEADER"
        )

class InvalidTokenException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="ERR_008",
            error_message="INVALID TOKEN"
        )

class UnauthenticatedException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="ERR_009",
            error_message="UNAUTHENTICATED"
        )

class InvalidAccountException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="ERR_010",
            error_message="INVALID ACCOUNT"
        )