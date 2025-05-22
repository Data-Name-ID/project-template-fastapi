from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.users.models import UserModel
from app.core.store import Store

required_bearer = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)

TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(required_bearer)]
OptionalTokenDep = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(optional_bearer),
]


def get_store(request: Request) -> Store:
    return request.app.state.store


StoreDep = Annotated[Store, Depends(get_store)]


async def user_dependency(token: TokenDep, store: StoreDep) -> UserModel:
    return await store.user_manager.fetch_user_from_access_token(token.credentials)


async def user_dependency_non_req(
    token: OptionalTokenDep,
    store: StoreDep,
) -> UserModel | None:
    if token is None:
        return None

    return await user_dependency(token=token, store=store)


UserDep = Annotated[UserModel, Depends(user_dependency)]
UserDepNonReq = Annotated[UserModel | None, Depends(user_dependency_non_req)]
