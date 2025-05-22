from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Cookie, Request, Response
from fastapi.responses import RedirectResponse

from app.api.users import errors
from app.api.users.models import UserModel
from app.api.users.schemas import UserCreate, UserLogin, UserPublic
from app.core.depends import StoreDep, UserDep
from app.core.jwt.schemas import AccessToken, RefreshToken, TokenCollection
from app.core.utils import build_responses

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post(
    "/signup",
    summary="Регистрация",
    response_description="Коллекция токенов доступа",
    description="""
    Устанавливает куку с refresh токеном,
    отправляет письмо с подтверждением на указанный email.
    """,
    responses=build_responses(
        errors.USER_CREATION_ERROR,
        errors.USER_ALREADY_EXISTS_ERROR,
    ),
)
async def sign_up(
    user_in: UserCreate,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    store: StoreDep,
) -> TokenCollection:
    is_email_exists = await store.user_accessor.exists_by_email(user_in.email)
    is_username_exists = await store.user_accessor.exists_by_username(user_in.username)

    if is_email_exists or is_username_exists:
        raise errors.USER_ALREADY_EXISTS_ERROR

    user_id = await store.user_accessor.create(user_in)

    if user_id is None:
        raise errors.USER_CREATION_ERROR

    background_tasks.add_task(
        store.user_manager.send_confirm_email,
        user_id=user_id,
        email=user_in.email,
        base_url=request.base_url,
    )

    token_collection = store.jwt.create_token_collection(user_id)
    store.user_manager.set_refresh_token_cookie(
        request=request,
        response=response,
        token=token_collection.refresh_token,
    )
    return token_collection


@router.post(
    "/signin",
    summary="Вход в систему",
    response_description="Коллекция токенов доступа",
    description="Устанавливает куку с refresh токеном.",
    responses=build_responses(errors.WRONG_EMAIL_OR_PASSWORD_ERROR),
)
async def sign_in(
    user_in: UserLogin,
    request: Request,
    response: Response,
    store: StoreDep,
) -> TokenCollection:
    if user_in._email:
        user = await store.user_accessor.fetch_by_email(user_in._email)
    elif user_in._username:
        user = await store.user_accessor.fetch_by_username(user_in._username)

    if user and user.validate_password(user_in.password):
        token_collection = store.jwt.create_token_collection(user.id)
        store.user_manager.set_refresh_token_cookie(
            request=request,
            response=response,
            token=token_collection.refresh_token,
        )
        return token_collection

    raise errors.WRONG_EMAIL_OR_PASSWORD_ERROR


@router.get(
    "/current",
    summary="Текущий пользователь",
    response_description="Текущий пользователь",
    response_model=UserPublic,
    responses=build_responses(
        errors.INVALID_TOKEN_ERROR,
        errors.UNACTIVATED_USER_ERROR,
        errors.USER_NOT_EXISTS_ERROR,
    ),
)
async def current_user(user: UserDep) -> UserModel:
    return user


@router.post(
    "/refresh",
    summary="Обновление токена",
    description="Использует refresh токен из куки либо из тела запроса.",
    response_description="Токен доступа",
    responses=build_responses(
        errors.INVALID_TOKEN_ERROR,
        errors.USER_NOT_EXISTS_ERROR,
    ),
)
async def refresh(
    store: StoreDep,
    credentials: RefreshToken | None = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> AccessToken:
    token = credentials.refresh_token if credentials is not None else refresh_token

    if token is not None:
        return await store.user_manager.refresh_access_token(token)

    raise errors.REFRESH_TOKEN_NOT_PROVIDED_ERROR


@router.get(
    "/confirm",
    summary="Подтверждение email",
    response_description="Перенаправление на главную страницу",
    responses=build_responses(
        errors.INVALID_TOKEN_ERROR,
        errors.USER_NOT_EXISTS_ERROR,
    ),
)
async def confirm_email(token: str, store: StoreDep) -> RedirectResponse:
    await store.user_manager.activate_user_by_token(token)
    return RedirectResponse(url="/profile")
