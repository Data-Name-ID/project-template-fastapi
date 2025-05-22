import re
import string

from app.core.config import StaticConfig


def validate_username_value(username: str) -> str:
    if len(username) < StaticConfig.USERNAME_MIN_LENGTH:
        msg = (
            "Имя пользователя должно состоять "
            f"минимум из {StaticConfig.USERNAME_MIN_LENGTH} символов"
        )
        raise ValueError(msg)

    if not re.fullmatch(r"\w+", username):
        msg = (
            "Имя пользователя может содержать "
            "только буквы, цифры и символ подчёркивания"
        )
        raise ValueError(msg)

    return username


def validate_password_value(password: str) -> str:
    if len(password) < StaticConfig.PASSWORD_MIN_LENGTH:
        msg = (
            "Пароль должен содержать "
            f"не менее {StaticConfig.PASSWORD_MIN_LENGTH} символов"
        )
        raise ValueError(msg)

    if not any(c.isupper() for c in password):
        msg = "Пароль должен содержать хотя бы одну заглавную букву"
        raise ValueError(msg)

    if not any(c.islower() for c in password):
        msg = "Пароль должен содержать хотя бы одну строчную букву"
        raise ValueError(msg)

    if not any(c.isdigit() for c in password):
        msg = "Пароль должен содержать хотя бы одну цифру"
        raise ValueError(msg)

    if not any(c in string.punctuation for c in password):
        msg = (
            "Пароль должен содержать хотя бы один специальный символ "
            f"из {string.punctuation}"
        )
        raise ValueError(msg)

    return password
