from pydantic import Field
from datetime import date
from pydantic import BaseModel, ConfigDict
from app.core.status import TaskStatus
from app.schemas.label_schemas import LabelResponse

class TaskBase(BaseModel):
    task_title: str = Field(min_length=1, max_length=255)
    task_info: str | None = None
    parent_task_id: int | None = None


class TaskUpdate(BaseModel):
    # Every field is optional: a PATCH body carries only what changes.
    task_title: str | None = Field(default=None, min_length=1, max_length=255)
    task_info: str | None = None
    status: TaskStatus | None = None
    cancel_reason: str | None =  Field(default=None,max_length= 100)


class TaskCreate(TaskBase):
    pass





class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    task_id: int
    status: TaskStatus
    created_at: date
    done_date: date | None
    cancel_reason: str | None
    owner_id: int
    labels: list[LabelResponse] = []
