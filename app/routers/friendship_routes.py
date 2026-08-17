from fastapi import APIRouter, Depends, status
from app.schemas.friendship_schemas import FriendshipCreate, FriendshipResponse, FriendshipUpdate, FriendResponse
from app.core.deps import CurrentUser
from app.db.session import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from app.services.friendship_service import (
    friendship_request_create,
    get_pending_requests,
    get_friends,
    friendship_request_or_deny,
    remove_friend
)



router = APIRouter(prefix="/friendships", tags=["friendship"])


@router.get("/pending", response_model=list[FriendshipResponse], status_code=status.HTTP_200_OK)
def get_all_pending_requests(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return get_pending_requests(db, user)

@router.get("", response_model=list[FriendResponse], status_code=status.HTTP_200_OK)
def get_all_friends(user: CurrentUser,db: Annotated[Session, Depends(get_db)] ):
    return get_friends(db, user)

@router.post("/request", response_model=FriendshipResponse, status_code= status.HTTP_201_CREATED)
def request(user: CurrentUser, friendship: FriendshipCreate, db: Annotated[Session, Depends(get_db)] ):
    return friendship_request_create(db, user, friendship)

@router.patch("/{requester_id}", response_model=FriendshipResponse, status_code= status.HTTP_200_OK)
def accept_or_deny_request(requester_id: int, friendship: FriendshipUpdate, user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    return friendship_request_or_deny(db,user,requester_id,friendship)

@router.delete("/{friend_id}", status_code=status.HTTP_204_NO_CONTENT )
def delete_friendship(friend_id: int, user: CurrentUser, db: Annotated[Session,Depends(get_db)]):
    return remove_friend(db,user,friend_id)


