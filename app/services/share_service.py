from sqlalchemy.orm import Session
from app import models
from fastapi import HTTPException, status
from sqlalchemy import select
from app.services.task_service import get_owned_task
from app.schemas.share_schemas import ShareCreate
from sqlalchemy import  or_, select, and_
from app.core.status import FriendshipStatus


def share_task(db: Session, user: models.User,task_id:int, share:ShareCreate) -> models.TaskShare:
   task= get_owned_task(db,user,task_id)#check if the task exists and user owns it. returns 404 if not.

   if task.parent_task_id is not None: # check if the shared task is the root task
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you can't share a subtask",
        )

   shared_user = db.execute(#get shared user
       select(models.User).where(
           models.User.username == share.shared_username
       )
   ).scalars().first()

   if shared_user is None:# check if the shared user exists
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared user not found",
        )
   if user.user_id == shared_user.user_id:# check if shared user is the sharing user
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target user cannot be yourself",
        )
   existing_friendship = db.execute(
        select(models.Friendship).where(
            or_(
                and_(models.Friendship.requester_id == user.user_id, models.Friendship.addressee_id == shared_user.user_id),
                and_(models.Friendship.requester_id == shared_user.user_id, models.Friendship.addressee_id == user.user_id),
            ),
            models.Friendship.status == FriendshipStatus.APPROVED
        )
    ).scalars().first()
   if existing_friendship is None: # check if the users are friends
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you dont have a friendship with the shared user",
        )
   existing_share = db.execute(
        select(models.TaskShare).where(
             models.TaskShare.shared_task_id == task_id,
             models.TaskShare.shared_user_id == shared_user.user_id
        )
   ).scalars().first()
   if existing_share is not None:#check if the task isn't already shared
                raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="task is already shared with that user",
        )
   new_share = models.TaskShare(
         shared_task_id = task_id,
         shared_user_id = shared_user.user_id
   )
   db.add(new_share)
   db.commit()
   db.refresh(new_share)
   return new_share
   



    