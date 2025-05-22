from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func


class BigIDMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
    )


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
    )
