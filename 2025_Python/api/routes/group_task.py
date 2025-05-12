from fastapi import APIRouter
from ..models import GroupTaskRequest
import state

router = APIRouter()


@router.post("/group_task")
async def group_task(request: GroupTaskRequest):
    iterations = request.iterations
    characters = state.characters.values()
    task = request.task_name
    args = request.args
    kwargs = request.kwargs

    for character in characters:
        state.task_manager.add_task(
            iterations, character, task, *args, **kwargs
        )

    return {"message": "Task added succesfully"}
