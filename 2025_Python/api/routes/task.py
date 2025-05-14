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

    await state.task_manager.add_task(
        character, task, iterations, *args, **kwargs
    )

    return {"message": "Task added succesfully"}