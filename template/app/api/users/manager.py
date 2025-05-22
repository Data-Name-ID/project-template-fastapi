from fastapi import Request, Response
from fastapi.datastructures import URL
from jwt import InvalidTokenError

from app.api.users import errors
from app.api.users.models import UserModel
from app.core.accessors import BaseAccessor
from app.core.jwt.schemas import AccessToken, TokenPayload, TokenType


class UserManager(BaseAccessor):
    def _decode_and_verify_token(
        self,
        *,
        token: str,
        expected_type: TokenType,
    ) -> TokenPayload:
        try:
            payload = self.store.jwt.decode_jwt(token)
        except InvalidTokenError as exc:
            raise errors.INVALID_TOKEN_ERROR from exc

        if payload.typ != expected_type.value:
            raise errors.INVALID_TOKEN_ERROR

        return payload

    async def _ensure_user_exists(self, user_id: int) -> None:
        if not await self.store.user_accessor.exists_by_id(user_id):
            raise errors.USER_NOT_EXISTS_ERROR

    async def _fetch_and_validate_user(self, user_id: int) -> UserModel:
        user = await self.store.user_accessor.fetch_by_id(user_id)

        if not user:
            raise errors.INVALID_TOKEN_ERROR

        if not user.activated:
            raise errors.UNACTIVATED_USER_ERROR

        return user

    async def fetch_user_from_access_token(self, token: str) -> UserModel:
        payload = self._decode_and_verify_token(
            token=token,
            expected_type=TokenType.ACCESS,
        )

        return await self._fetch_and_validate_user(payload._user_id)

    async def refresh_access_token(self, token: str) -> AccessToken:
        payload = self._decode_and_verify_token(
            token=token,
            expected_type=TokenType.REFRESH,
        )

        await self._ensure_user_exists(payload._user_id)

        new_token = self.store.jwt.create_access_token(
            payload._user_id,
            rjti=payload.jti,
        ).token

        return AccessToken(access_token=new_token)

    async def activate_user_by_token(self, token: str) -> None:
        payload = self._decode_and_verify_token(
            token=token,
            expected_type=TokenType.EMAIL_CONFIRM,
        )

        await self._ensure_user_exists(payload._user_id)
        await self.store.user_accessor.activate(payload._user_id)

    def set_refresh_token_cookie(
        self,
        *,
        request: Request,
        response: Response,
        token: str,
    ) -> None:
        response.set_cookie(
            key="refresh_token",
            value=token,
            httponly=True,
            secure=request.url.scheme == "https",
            max_age=self.store.jwt.refresh_token_expiration_seconds,
        )

    async def send_confirm_email(
        self,
        *,
        user_id: int,
        email: str,
        base_url: str | URL,
    ) -> None:
        token = self.store.jwt.create_email_confirm_token(user_id).token
        confirm_url = f"{base_url}api/auth/confirm?token={token}"

        await self.store.email.send_email(
            recipient=email,
            title="Подтверждение аккаунта",
            template="email_confirm.html",
            base_url=base_url,
            url=confirm_url,
        )
