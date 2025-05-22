from asyncio import current_task
from collections.abc import AsyncGenerator, Callable, Sequence
from contextlib import asynccontextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Any, TypeVar, overload

from sqlalchemy import MetaData, Row
from sqlalchemy.engine import CursorResult, Result, ScalarResult
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.base import Executable
from sqlalchemy.sql.dml import UpdateBase
from sqlalchemy.sql.selectable import TypedReturnsRows

from app.core.accessors import BaseAccessor
from app.core.store import Store

_T = TypeVar("_T", bound=Any)


class BaseModel(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": ("fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"),
            "pk": "pk_%(table_name)s",
        },
    )


class DatabaseAccessor(BaseAccessor):
    def __init__(self, store: Store) -> None:
        super().__init__(store)

        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker | None = None
        self._current_session: ContextVar[AsyncSession | None] = ContextVar(
            "current_session",
            default=None,
        )

    async def connect(self) -> None:
        self._engine = create_async_engine(
            url=self.store.config.db.url,
            echo=self.store.config.db.echo,
            echo_pool=self.store.config.db.echo_pool,
            pool_size=self.store.config.db.pool_size,
            max_overflow=self.store.config.db.max_overflow,
        )
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def disconnect(self) -> None:
        if self._engine is None:
            return

        await self._engine.dispose()
        self._engine = None

    @property
    def session_maker(self) -> async_sessionmaker:
        if self._session_maker is None:
            msg = "DatabaseAccessor is not connected"
            raise RuntimeError(msg)

        return self._session_maker

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        scoped_session = async_scoped_session(
            session_factory=self.session_maker,
            scopefunc=current_task,
        )

        async with scoped_session() as session:
            token = self._current_session.set(session)

            yield session
            await session.commit()

            self._current_session.reset(token)
            await scoped_session.remove()

    def get_current_session(self) -> AsyncSession | None:
        return self._current_session.get()

    @overload
    async def execute(
        self,
        statement: TypedReturnsRows[_T],
    ) -> Result[_T]: ...

    @overload
    async def execute(
        self,
        statement: UpdateBase,
    ) -> CursorResult[Any]: ...

    @overload
    async def execute(
        self,
        statement: Executable,
    ) -> Result[Any]: ...

    async def execute(
        self,
        statement: Executable,
    ) -> Result[Any]:
        session = self.get_current_session()

        if session:
            return await session.execute(statement)

        async with self.session() as session:
            return await session.execute(statement)

    async def scalar(self, statement: Executable) -> Any:
        return (await self.execute(statement)).scalar()

    async def scalars(self, statement: Executable) -> ScalarResult[Any]:
        return (await self.execute(statement)).scalars()

    async def one(self, statement: Executable) -> Row[Any]:
        return (await self.execute(statement)).one()

    async def one_or_none(self, statement: Executable) -> Row[Any] | None:
        return (await self.execute(statement)).one_or_none()

    async def first(self, statement: Executable) -> Row[Any] | None:
        return (await self.execute(statement)).first()

    async def all(self, statement: Executable) -> Sequence[Row[Any]]:
        return (await self.execute(statement)).all()


@asynccontextmanager
async def single_session(db: DatabaseAccessor) -> AsyncGenerator[AsyncSession, None]:
    session = db.get_current_session()

    if session:
        yield session
    else:
        async with db.session() as session:
            yield session


@asynccontextmanager
async def transaction(db: DatabaseAccessor) -> AsyncGenerator[AsyncSession, None]:
    session = db.get_current_session()

    if session:
        async with session.begin_nested():
            yield session
    else:
        async with db.session() as session, session.begin():
            yield session


def with_single_session(method: Callable) -> Callable:
    @wraps(method)
    async def wrapper(self: BaseAccessor, *args: Any, **kwargs: Any) -> Any:
        async with single_session(self.store.db):
            return await method(self, *args, **kwargs)

    return wrapper


def with_transaction(method: Callable) -> Callable:
    @wraps(method)
    async def wrapper(self: BaseAccessor, *args: Any, **kwargs: Any) -> Any:
        async with transaction(self.store.db):
            return await method(self, *args, **kwargs)

    return wrapper
