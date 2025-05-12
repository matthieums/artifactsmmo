from fastapi import APIRouter

from ..models import TaskRequest
import state

router = APIRouter()


@router.post("/task")
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