from pydantic import BaseModel, ConfigDict, Field

# A 6-digit hex color, e.g. "#3B82F6". Validated here so the service layer
# can assume the color is already well-formed.
HEX_COLOR = r"^#[0-9A-Fa-f]{6}$"


class LabelBase(BaseModel):
    label_name: str = Field(min_length=1, max_length=50)
    label_color: str = Field(pattern=HEX_COLOR)


class LabelCreate(LabelBase):
    pass


class LabelUpdate(BaseModel):
    # Every field is optional: a PATCH body carries only what changes.
    label_name: str | None = Field(default=None, min_length=1, max_length=50)
    label_color: str | None = Field(default=None, pattern=HEX_COLOR)


class LabelResponse(LabelBase):
    model_config = ConfigDict(from_attributes=True)
    label_id: int