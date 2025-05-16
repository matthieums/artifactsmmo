from fastapi import APIRouter
from ..models import GroupTaskRequest
import state
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/group_task")
async def group_task(request: GroupTaskRequest):
    iterations = request.iterations
    characters = state.characters.values()
    task = request.task_name
    args = request.args
    kwargs = request.kwargs

    if task == "deposit_all":
        task = "deposit"
        for character in characters:
            for item, qty in character.inventory:
                kwargs["item"] = item
                kwargs["quantity"] = qty
                await state.task_manager.add_task(
                    character, task, iterations, *args, **kwargs
                )
    else:
        for character in characters:
            await state.task_manager.add_task(
                character, task, iterations, *args, **kwargs
            )

    return {"message": "Task added succesfully"}
