from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.db.session import get_db
from app.schemas.label_schemas import LabelCreate, LabelResponse, LabelUpdate
from app.schemas.task_schemas import TaskResponse
from app.services.task_service import to_task_response
from app.services.label_service import (
    add_label_to_task,
    create_label,
    delete_label,
    get_labels,
    get_owned_label,
    remove_label_from_task,
    update_label,
)

router = APIRouter(prefix="/labels", tags=["labels"])


@router.get("", response_model=list[LabelResponse])
def list_labels(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return get_labels(db, user)


@router.post("", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
def add_label(label: LabelCreate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return create_label(db, user, label)


@router.get("/{label_id}", response_model=LabelResponse)
def read_label(label_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return get_owned_label(db, user, label_id)


@router.patch("/{label_id}", response_model=LabelResponse)
def edit_label(label_id: int, changes: LabelUpdate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return update_label(db, user, label_id, changes)


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_label(label_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> None:
    return delete_label(db, user, label_id)


task_labels_router = APIRouter(prefix="/tasks", tags=["labels"])


@task_labels_router.post(
    "/{task_id}/labels/{label_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def attach_label(task_id: int, label_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return to_task_response(add_label_to_task(db, user, task_id, label_id), user)


@task_labels_router.delete(
    "/{task_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT
)
def detach_label(task_id: int, label_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> None:
    return remove_label_from_task(db, user, task_id, label_id)
