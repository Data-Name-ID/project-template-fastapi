from passlib.context import CryptContext
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import StaticConfig
from app.core.db import BaseModel
from app.core.models.mixins import CreatedAtMixin, IDMixin, UpdatedAtMixin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserModel(IDMixin, CreatedAtMixin, UpdatedAtMixin, BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(StaticConfig.NAME_STR_LENGTH),
        unique=True,
    )
    email: Mapped[str] = mapped_column(
        String(StaticConfig.CREDENTIALS_STR_LENGTH),
        unique=True,
    )
    password: Mapped[str] = mapped_column(String(StaticConfig.CREDENTIALS_STR_LENGTH))

    activated: Mapped[bool] = mapped_column(default=False)

    def validate_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
