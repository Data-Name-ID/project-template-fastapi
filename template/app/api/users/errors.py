from fastapi import HTTPException, status

INVALID_TOKEN_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Недействительный токен",
)
REFRESH_TOKEN_NOT_PROVIDED_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Refresh токен не был предоставлен",
)
UNACTIVATED_USER_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Пользователь не активирован",
)
USER_ALREADY_EXISTS_ERROR = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователь уже зарегистрирован",
)
USER_NOT_EXISTS_ERROR = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователя не существует",
)
USER_WITH_USERNAME_NOT_EXISTS_ERROR = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователя с таким никнеймом не существует",
)
USER_WITH_USERNAME_ALREADY_EXISTS_ERROR = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователя с таким никнейм уже существует",
)
WRONG_EMAIL_OR_PASSWORD_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный email или пароль",
)
USER_CREATION_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Ошибка создания пользователя",
)
