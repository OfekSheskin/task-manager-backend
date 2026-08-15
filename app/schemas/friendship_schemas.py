from pydantic import BaseModel, ConfigDict
from app.core.status import FriendshipStatus
from typing import Literal




class FriendshipBase(BaseModel):
    pass

class FriendshipCreate(FriendshipBase):
    addressee_username: str

class FriendshipUpdate(FriendshipBase):
    status: Literal[FriendshipStatus.APPROVED, FriendshipStatus.DENIED]

class FriendshipResponse(FriendshipBase):
    model_config = ConfigDict(from_attributes=True)
    requester_id: int
    addressee_id: int
    status: FriendshipStatus

class FriendResponse(BaseModel):
    """The *other* user in an approved friendship, from the current user's side."""
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    username: str





    