from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import state
from pydantic import BaseModel
from typing import List, Any, Dict
import logging


logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def get_characters():
    return state.characters


class TaskRequest(BaseModel):
    iterations: int
    character_index: int
    function: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}


@app.post("/task")
async def task(request: TaskRequest):
    iterations = request.iterations
    character = state.characters[request.character_index]
    function = request.function
    args = request.args
    kwargs = request.kwargs

    state.task_manager.add_task(
        iterations, character, function, *args, **kwargs
    )

    return {"message": "Task added succesfully"}