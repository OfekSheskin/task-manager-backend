from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.schemas.task_schemas import TaskCreate


def get_task(db: Session, user: models.User, task_id: int) -> models.Task:

    task = db.execute(
        select(models.Task).where(
            models.Task.task_id == task_id,
            models.Task.owner_id == user.user_id,
        )
    ).scalars().first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


def get_tasks(db: Session, user: models.User) -> list[models.Task]:
    tasks = db.execute(
        select(models.Task).where(models.Task.owner_id == user.user_id)
    ).scalars().all()
    return list(tasks)


def create_task(db: Session, user: models.User, task: TaskCreate) -> models.Task:
    if task.parent_task_id is not None:
        # Called purely as a guard: raises 404 if the parent is missing or is
        # not this user's, so a subtask can never hang off a stranger's task.
        get_task(db, user, task.parent_task_id)

    new_task = models.Task(
        task_title=task.task_title,
        task_info=task.task_info,
        owner_id=user.user_id,
        parent_task_id=task.parent_task_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
