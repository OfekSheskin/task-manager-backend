
from sqlalchemy import CheckConstraint, Column, ForeignKey, Table

from app.db.base import Base

blocking_tasks = Table(
    "blocking_tasks",
    Base.metadata,
    Column(
        "blocking_task_id",
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "blocked_task_id",
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        primary_key=True,
    ),

    CheckConstraint(
        "blocking_task_id <> blocked_task_id", name="ck_blocking_tasks_no_self_block"
    ),
)
