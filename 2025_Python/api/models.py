from pydantic import BaseModel
from typing import List, Any, Dict


class TaskRequest(BaseModel):
    iterations: int
    character_name: str
    task_name: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}


class GroupTaskRequest(BaseModel):
    iterations: int
    task_name: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}
