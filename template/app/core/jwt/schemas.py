from enum import StrEnum, auto

from pydantic import BaseModel, PrivateAttr, ValidationInfo, field_validator


class TokenType(StrEnum):
    ACCESS = auto()
    REFRESH = auto()
    EMAIL_CONFIRM = auto()
    RESET_PASSWORD = auto()


class AccessToken(BaseModel):
    access_token: str


class RefreshToken(BaseModel):
    refresh_token: str


class Token(BaseModel):
    token: str
    jti: str


class TokenCollection(BaseModel):
    type: str = "Bearer"

    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    typ: TokenType
    jti: str
    iat: float
    exp: float
    sub: str
    rjti: str | None = None

    _user_id: int = PrivateAttr()

    @field_validator("sub")
    @classmethod
    def check_login(cls, sub: str, info: ValidationInfo) -> str:
        info.data["_user_id"] = int(sub)

        return sub
