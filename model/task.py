# Model
import pydantic
import typing

class Task(pydantic.BaseModel):
    id: int | str
    name: str
    is_done: bool

# TODO: set the request body optional for update operation
class TaskCreateRequestBody(pydantic.BaseModel):
    name: str
    is_done: bool = False

class TaskOptionalRequestBody(pydantic.BaseModel):
    name: typing.Optional[str] = ""
    is_done: typing.Optional[bool] = False