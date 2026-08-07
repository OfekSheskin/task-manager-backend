from pydantic import Field
from datetime import date
from pydantic import BaseModel, ConfigDict
from app.core.status import Status

class TaskBase(BaseModel):
    task_title: str = Field(min_length=1, max_length=255)
    task_info: str | None = None
    parent_task_id: int | None = None



class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    task_id: int
    status: Status
    created_at: date
    done_date: date | None
    cancel_reason: str | None
    owner_id: int
