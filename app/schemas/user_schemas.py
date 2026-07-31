from pydantic import BaseModel, ConfigDict, Field
from datetime import date

class UserBase(BaseModel):
    username: str = Field(min_length=5, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=50)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    created_at: date

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

