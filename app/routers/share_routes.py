from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.db.session import get_db
from app.schemas.share_schemas import ShareCreate, ShareUserResponse
from app.services.share_service import share_task, unshare_task, list_shares

router = APIRouter(prefix="/tasks", tags=["shares"])


@router.post("/{task_id}/shares", response_model=ShareUserResponse, status_code=status.HTTP_201_CREATED)
def share_single_task(task_id: int, share: ShareCreate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return share_task(db, user, task_id, share)

@router.delete("/{task_id}/shares/{shared_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_share(task_id: int, shared_user_id: int, user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> None:
    return unshare_task(db, user, task_id, shared_user_id)

@router.get("/{task_id}/shares", response_model= list[ShareUserResponse], status_code= status.HTTP_200_OK)
def shares(task_id: int, user: CurrentUser,db: Annotated[Session, Depends(get_db)] ):
    return list_shares(db,user,task_id)
