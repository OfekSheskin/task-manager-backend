from sqlalchemy.orm import Session
from app import models
from app.schemas.friendship_schemas import FriendshipCreate
from sqlalchemy import or_, select, and_
from fastapi import HTTPException, status
from app.core.status import FriendshipStatus



def friendship_request_create(db: Session, user: models.User, friendship: FriendshipCreate) -> models.Friendship:

    addressee = db.execute(
        select(models.User).where(models.User.username == friendship.addressee_username )
    ).scalars().first()
    if addressee is None:#check if the addressee user exists
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "addressee user doesn't exist",
        )
    if addressee.user_id == user.user_id:# the DB check constraint would only give a 500
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "you cannot send a friendship request to yourself",
        )

    existing_friendship = db.execute(
        select(models.Friendship).where(
            or_(
                and_(models.Friendship.requester_id == user.user_id, models.Friendship.addressee_id == addressee.user_id),
                and_(models.Friendship.requester_id == addressee.user_id, models.Friendship.addressee_id == user.user_id),
            )
        )
    ).scalars().first()
    if existing_friendship is not None:# check if the friendship request already exists
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "the friendship request already exists"
        )

    new_friendship = models.Friendship(
        requester_id =  user.user_id,
        addressee_id = addressee.user_id
        
    )
    db.add(new_friendship)
    db.commit()
    db.refresh(new_friendship)
    return new_friendship
    
def get_pending_requests(db: Session, user: models.User) -> list[models.Friendship]:
    pending_requests = db.execute(
        select(models.Friendship).where(
            models.Friendship.addressee_id == user.user_id,
            models.Friendship.status == FriendshipStatus.PENDING,
            )
    ).scalars().all()
    return list(pending_requests)
