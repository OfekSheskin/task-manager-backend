from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.db.session import get_db

from app.schemas.task_schemas import TaskResponse, TaskCreate, TaskUpdate
from app.services.task_service import (
    create_task,
    get_tasks,
    get_task,
    update_task,
    delete_task,
    to_task_response,
)

router =  APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_all_tasks(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return [to_task_response(task, user) for task in get_tasks(db, user)]

@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_single_task(task_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return to_task_response(get_task(db, user, task_id), user)

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_new_task(task: TaskCreate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return to_task_response(create_task(db, user, task), user)

@router.patch("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_single_task(task_id: int, task: TaskUpdate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return to_task_response(update_task(db, user, task_id, task), user)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_task(task_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> None:
    delete_task(db, user, task_id)



