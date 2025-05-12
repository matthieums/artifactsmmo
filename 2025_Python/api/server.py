
from fastapi import FastAPI, Request
import logging
import config
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import characters, task, task_queues, group_task

logger = logging.getLogger(__name__)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    **config.CORS_CONFIG
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

app.include_router(characters.router)
app.include_router(task.router)
app.include_router(task_queues.router)
app.include_router(group_task.router)
