# Model
import pydantic


class Task(pydantic.BaseModel):
    id: int | str
    name: str
    is_done: bool

# TODO: set the request body optional for update operation
class TaskCreateRequestBody(pydantic.BaseModel):
    name: str
    is_done: bool = False