
from datetime import date
from sqlalchemy import Date, String, func, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.core.status import TaskStatus
from app.models.label import Label
from app.models.task_label import task_labels
from app.models.blocking_task import blocking_tasks




class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(primary_key=True)
    task_title: Mapped[str] = mapped_column(String(255), index=True)
    task_info:  Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[date] = mapped_column(
        Date, server_default=func.current_date()
    )
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus, name="status"), default=TaskStatus.TO_DO, index=True)
    cancel_reason: Mapped[str | None] = mapped_column(String(100))
    done_date: Mapped[date | None] = mapped_column(
        Date
    )
    parent_task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.task_id" , ondelete="CASCADE"), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)

    labels: Mapped[list[Label]] = relationship(
        secondary=task_labels, lazy="selectin"
    )

    # Self-referential many-to-many over blocking_tasks. The same table is read
    # from both directions, so each side has to say explicitly which column it
    # starts from and which it lands on:
    #   blockers -> the tasks that hold THIS task up
    #   blocking -> the tasks THIS task is holding up
    blockers: Mapped[list["Task"]] = relationship(
        secondary=blocking_tasks,
        primaryjoin=lambda: Task.task_id == blocking_tasks.c.blocked_task_id,
        secondaryjoin=lambda: Task.task_id == blocking_tasks.c.blocking_task_id,
        back_populates="blocking",
        lazy="selectin",
    )
    blocking: Mapped[list["Task"]] = relationship(
        secondary=blocking_tasks,
        primaryjoin=lambda: Task.task_id == blocking_tasks.c.blocking_task_id,
        secondaryjoin=lambda: Task.task_id == blocking_tasks.c.blocked_task_id,
        back_populates="blockers",
        lazy="selectin",
    )
