from fastapi import FastAPI
import state
import logging
from .models import TaskRequest

logger = logging.getLogger(__name__)
app = FastAPI()


@app.get("/characters")
async def get_characters():
    return state.characters


@app.get("/task_queues")
async def get_queues():
    queues = state.task_manager.task_queues
    result = {
        character.name: [
            {
                "taskName": task.method.__name__,
                "args": task.args,
                "kwargs": task.kwargs
            }
            for task in tasks
        ]
        for character, tasks in queues.items()
    }
    return result


@app.post("/task")
async def task(request: TaskRequest):
    iterations = request.iterations
    character = state.characters[request.character_name]
    task = request.task_name
    args = request.args
    kwargs = request.kwargs

    state.task_manager.add_task(
        iterations, character, task, *args, **kwargs
    )

    return {"message": "Task added succesfully"}