from sqlalchemy.orm import Session
from app import models
from app.schemas.friendship_schemas import FriendshipCreate, FriendshipUpdate
from sqlalchemy import case, or_, select, and_
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
        if existing_friendship.status != FriendshipStatus.DENIED:
           raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail= "the friendship request already exists"
            )

        db.delete(existing_friendship)
        db.flush()

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

def get_friends(db: Session, user: models.User) -> list[models.User]:

    friend_id = case(
        (models.Friendship.requester_id == user.user_id, models.Friendship.addressee_id),
        else_=models.Friendship.requester_id,
    )

    friends = db.execute(
        select(models.User)
        .join(models.Friendship, models.User.user_id == friend_id)
        .where(
            or_(
                models.Friendship.requester_id == user.user_id,
                models.Friendship.addressee_id == user.user_id,
            ),
            models.Friendship.status == FriendshipStatus.APPROVED,
        )
        .order_by(models.User.username)
    ).scalars().all()
    return list(friends)
def friendship_request_or_deny(db: Session, user: models.User, user_id: int, friendship: FriendshipUpdate )-> models.Friendship:
    if user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= "the request user and addressee can't be the same person",
        )

    if friendship.status == FriendshipStatus.PENDING:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "the friendship is already approved or denied",
        )
    pending_request = db.execute(
        select(models.Friendship).where(
            models.Friendship.addressee_id == user.user_id,
            models.Friendship.requester_id == user_id,
            models.Friendship.status == FriendshipStatus.PENDING
        )
    ).scalars().first()
    if pending_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "friendship request doesn't exist",
        )
    data = friendship.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(pending_request, field, value)

    db.commit()
    return pending_request
def remove_friend(db: Session, user: models.User,friend_id:int) -> None:

    existing_friendship = db.execute(
        select(models.Friendship).where(
            or_(
                and_(models.Friendship.requester_id == user.user_id, models.Friendship.addressee_id == friend_id),
                and_(models.Friendship.requester_id == friend_id, models.Friendship.addressee_id == user.user_id),
            ),
            models.Friendship.status == FriendshipStatus.APPROVED
        )
    ).scalars().first()

    if existing_friendship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "friendship doesn't exist or isnt approved yet",
        )

    shared_task = db.execute(
        select(models.TaskShare.shared_task_id)
        .join(models.Task, models.Task.task_id == models.TaskShare.shared_task_id)
        .where(
            or_(
                and_(models.Task.owner_id == user.user_id, models.TaskShare.shared_user_id == friend_id),
                and_(models.Task.owner_id == friend_id, models.TaskShare.shared_user_id == user.user_id),
            )
        )
        .limit(1)
    ).scalars().first()

    if shared_task is not None:# friends can't be removed while a task is shared between them
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= "you cannot remove a friend while you share a task",
        )

    db.delete(existing_friendship)
    db.commit()







    
    
