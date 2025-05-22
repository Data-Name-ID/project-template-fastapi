from sqlalchemy import exists, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import load_only

from app.api.users.models import UserModel
from app.api.users.schemas import UserCreate
from app.core.accessors import BaseAccessor


class UserAccessor(BaseAccessor):
    async def create(self, user_in: UserCreate) -> int | None:
        stmt = (
            insert(UserModel)
            .values(
                **user_in.model_dump(exclude={"password"}),
                password=UserModel.hash_password(user_in.password),
            )
            .returning(UserModel.id)
        )
        return await self.store.db.scalar(stmt)

    async def exists_by_id(self, user_id: int) -> bool:
        stmt = select(exists().where(UserModel.id == user_id))
        return await self.store.db.scalar(stmt)

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(exists().where(UserModel.email == email))
        return await self.store.db.scalar(stmt)

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(exists().where(UserModel.username == username))
        return await self.store.db.scalar(stmt)

    async def fetch_by_id(self, user_id: int) -> UserModel | None:
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(
                load_only(
                    UserModel.activated,
                    UserModel.username,
                ),
            )
        )
        return await self.store.db.scalar(stmt)

    async def fetch_by_email(self, email: str) -> UserModel | None:
        stmt = (
            select(UserModel)
            .where(UserModel.email == email)
            .options(load_only(UserModel.id, UserModel.password))
        )
        return await self.store.db.scalar(stmt)

    async def fetch_by_username(self, username: str) -> UserModel | None:
        stmt = (
            select(UserModel)
            .where(UserModel.username == username)
            .options(load_only(UserModel.id, UserModel.password))
        )
        return await self.store.db.scalar(stmt)

    async def activate(self, user_id: int) -> None:
        stmt = update(UserModel).where(UserModel.id == user_id).values(activated=True)
        await self.store.db.execute(stmt)
