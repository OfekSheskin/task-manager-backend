from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Label(Base):
    __tablename__ = "labels"

    label_id: Mapped[int] = mapped_column(primary_key=True)
    label_name: Mapped[str] = mapped_column(String(50), index=True)
    label_color: Mapped[str] = mapped_column(String(7))  # hex, e.g. "#3B82F6"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True
    )
