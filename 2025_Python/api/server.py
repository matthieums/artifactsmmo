
from fastapi import FastAPI
import logging
import config
from fastapi.middleware.cors import CORSMiddleware

from api.routes import characters, task, task_queues, group_task

logger = logging.getLogger(__name__)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    **config.CORS_CONFIG
)

app.include_router(characters.router)
app.include_router(task.router)
app.include_router(task_queues.router)
app.include_router(group_task.router)
