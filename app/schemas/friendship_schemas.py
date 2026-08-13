from pydantic import BaseModel, ConfigDict
from app.core.status import FriendshipStatus



class FriendshipBase(BaseModel):
    pass

class FriendshipCreate(FriendshipBase):
    addressee_username: str

class FriendshipResponse(FriendshipBase):
    model_config = ConfigDict(from_attributes=True)
    requester_id: int
    addressee_id: int 
    status: FriendshipStatus



    