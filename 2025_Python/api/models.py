from pydantic import BaseModel, Field
from typing import List, Any, Dict


class BaseTaskRequest(BaseModel):
    iterations: int
    task_name: str
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)


class TaskRequest(BaseTaskRequest):
    character_name: str


class GroupTaskRequest(BaseTaskRequest):
    pass
