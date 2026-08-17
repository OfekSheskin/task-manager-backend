from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.db.session import get_db
from app.schemas.share_schemas import ShareCreate, ShareResponse
from app.services.share_service import share_task

router = APIRouter(prefix="/tasks", tags=["shares"])


@router.post("/{task_id}/shares", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
def share_single_task(task_id: int, share: ShareCreate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return share_task(db, user, task_id, share)
