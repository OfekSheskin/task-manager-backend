from pydantic import BaseModel, ConfigDict


class ShareBase(BaseModel):
    pass

class ShareCreate(ShareBase):
    shared_username: str    



class ShareUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    username: str
