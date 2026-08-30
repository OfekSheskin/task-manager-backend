from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.db.session import get_db

from app.schemas.task_schemas import TaskResponse, TaskCreate, TaskUpdate
from app.services.task_service import (
    add_blocker,
    create_task,
    get_blockers,
    remove_blocker,
    get_tasks,
    get_task,
    update_task,
    delete_task,
    to_task_response,
)

router =  APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_all_tasks(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return [to_task_response(db, task, user) for task in get_tasks(db, user)]

@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_single_task(task_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return to_task_response(db, get_task(db, user, task_id), user)

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_new_task(task: TaskCreate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return to_task_response(db, create_task(db, user, task), user)

@router.patch("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_single_task(task_id: int, task: TaskUpdate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return to_task_response(db, update_task(db, user, task_id, task), user)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_task(task_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> None:
    delete_task(db, user, task_id)


# Blocking dependencies. 
@router.get("/{task_id}/blockers", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def list_task_blockers(task_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return [to_task_response(db, blocker, user) for blocker in get_blockers(db, user, task_id)]


@router.post("/{task_id}/blockers/{blocker_id}", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def add_task_blocker(task_id: int, blocker_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return to_task_response(db, add_blocker(db, user, task_id, blocker_id), user)


@router.delete("/{task_id}/blockers/{blocker_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def remove_task_blocker(task_id: int, blocker_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return to_task_response(db, remove_blocker(db, user, task_id, blocker_id), user)
