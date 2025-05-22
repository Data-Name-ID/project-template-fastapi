from pydantic import BaseModel, EmailStr, PrivateAttr, ValidationInfo, field_validator

from app.core import validators


class PasswordValidatorMixin(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def check_password(cls, password: str) -> str:
        return validators.validate_password_value(password)


class UserBase(BaseModel):
    email: EmailStr
    username: str

    @field_validator("username")
    @classmethod
    def check_username(cls, username: str) -> str:
        return validators.validate_username_value(username)


class UserCreate(PasswordValidatorMixin, UserBase):
    pass


class UserLogin(PasswordValidatorMixin, BaseModel):
    login: EmailStr | str
    password: str

    _email: EmailStr | None = PrivateAttr(default=None)
    _username: str | None = PrivateAttr(default=None)

    @field_validator("login")
    @classmethod
    def check_login(cls, login: str, info: ValidationInfo) -> str:
        if "@" not in login:
            info.data["_username"] = validators.validate_username_value(login)
        else:
            info.data["_email"] = login

        return login


class UserUpdate(BaseModel):
    username: str


class UserUpdateEmail(BaseModel):
    email: EmailStr


class UserUpdatePassword(PasswordValidatorMixin, BaseModel):
    password: str


class UserPublic(BaseModel):
    username: str
