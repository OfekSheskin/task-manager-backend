

from sqlalchemy import Column, ForeignKey, Table

from app.db.base import Base

task_labels = Table(
    "task_labels",
    Base.metadata,
    Column(
        "task_id",
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "label_id",
        ForeignKey("labels.label_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    
)
