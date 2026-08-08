from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date
from app import models
from app.schemas.task_schemas import TaskCreate, TaskUpdate
from app.core.status import Status


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
        # Called as a guard: raises 404 if the parent is missing or is
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


def update_task(
    db: Session, user: models.User, task_id: int, task: TaskUpdate) -> models.Task:
    existing = get_task(db, user, task_id) 
    data = task.model_dump(exclude_unset=True)

    if "parent_task_id" in data:
        _check_parent_change(db, user, existing, data["parent_task_id"])

    if "status" in data:
        _apply_status_change(db, existing, data["status"])


    for field, value in data.items():
        setattr(existing, field, value)

    db.commit()
    return existing


def delete_task(db: Session, user: models.User, task_id: int) -> None:
    task = get_task(db, user, task_id)
    db.delete(task)
    db.commit()






#helper functions
def _check_parent_change(#helper function to apply parent rules when updating a task
    db: Session, user: models.User, task: models.Task, new_parent_id: int | None
) -> None:

    if new_parent_id is None:
        return

    if new_parent_id == task.task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A task cannot be its own parent",
        )

    # Raises 404 if the parent is missing or is not this user's.
    ancestor = get_task(db, user, new_parent_id)

    # Walk up from the new parent. Meeting `task` on the way to the root means
    # the new parent is one of its descendants.
    while ancestor.parent_task_id is not None:
        if ancestor.parent_task_id == task.task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A task cannot be moved under one of its own subtasks",
            )
        ancestor = get_task(db, user, ancestor.parent_task_id)

def _apply_status_change(
    db: Session,  task: models.Task, new_status: str   
)-> None:
    if new_status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="a status cannot be null"
        )
    if new_status == Status.DONE:
        task.done_date = date.today()
        return

    if new_status == Status.TO_DO:
        task.done_date = None
        return

    if new_status == Status.CANCELLED:
        task.done_date = None

        return


