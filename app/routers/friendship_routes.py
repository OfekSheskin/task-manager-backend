from fastapi import APIRouter, Depends, status
from app.schemas.friendship_schemas import FriendshipCreate, FriendshipResponse
from app.core.deps import CurrentUser
from app.db.session import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from app.services.friendship_service import friendship_request_create, get_pending_requests



router = APIRouter(prefix="/friendships", tags=["friendship"])


@router.get("/pending", response_model=list[FriendshipResponse], status_code=status.HTTP_200_OK)
def get_all_pending_requests(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return get_pending_requests(db, user)


@router.post("/request", response_model=FriendshipResponse, status_code= status.HTTP_201_CREATED)
def request(user: CurrentUser, friendship: FriendshipCreate, db: Annotated[Session, Depends(get_db)] ):
    return friendship_request_create(db, user, friendship)

