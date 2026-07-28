from datetime import date

from sqlalchemy import Date, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[date] = mapped_column(
        Date, server_default=func.current_date()
    )
