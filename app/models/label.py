from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Label(Base):
    __tablename__ = "labels"
    __table_args__ = (
        # A user cannot have two labels with the same name; different users can.
        UniqueConstraint("user_id", "label_name", name="uq_labels_user_id_label_name"),
    )

    label_id: Mapped[int] = mapped_column(primary_key=True)
    label_name: Mapped[str] = mapped_column(String(50), index=True)
    label_color: Mapped[str] = mapped_column(String(7))  # hex, e.g. "#3B82F6"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True
    )
