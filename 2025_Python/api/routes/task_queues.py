from fastapi import APIRouter
import state

router = APIRouter()


@router.get("/task_queues")
async def get_queues():
    queues = state.task_manager.task_queues
    result = {
        character_name: [
            {
                "taskName": task.method.__name__,
                "args": task.args,
                "kwargs": task.kwargs
            }
            for task in tasks
        ]
        for character_name, tasks in queues.items()
    }
    return result