from fastapi import FastAPI
import state
import logging


logger = logging.getLogger(__name__)
app = FastAPI()



@app.get("/")
async def get_characters():
    return state.characters


class TaskRequest(BaseModel):
    iterations: int
    character_name: str
    function: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}


@app.post("/task")
async def task(request: TaskRequest):
    iterations = request.iterations
    character = state.characters[request.character_name]
    function = request.function
    args = request.args
    kwargs = request.kwargs

    state.task_manager.add_task(
        iterations, character, function, *args, **kwargs
    )

    return {"message": "Task added succesfully"}