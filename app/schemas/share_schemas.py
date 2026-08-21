from pydantic import BaseModel, ConfigDict
from typing import Literal


class ShareBase(BaseModel):
    pass

class ShareCreate(ShareBase):
    shared_username: str    

class ShareResponse(ShareBase):
    model_config = ConfigDict(from_attributes=True)
    shared_task_id: int
    shared_user_id: int

class ShareUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    username: str
