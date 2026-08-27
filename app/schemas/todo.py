from pydantic import BaseModel, ConfigDict, Field

class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    is_completed: bool

    model_config = ConfigDict(from_attributes=True)

class TodoUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=500
    )
    is_completed: bool | None = None