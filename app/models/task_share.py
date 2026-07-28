from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TaskShare(Base):


    __tablename__ = "task_shares"

    shared_task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.task_id", ondelete="CASCADE"), primary_key=True
    )
    shared_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
