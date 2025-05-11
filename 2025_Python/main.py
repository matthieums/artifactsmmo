from __future__ import annotations
import asyncio
import config
import logging
from utils.initialization import (
    initialize_bank, initialize_characters,
    initialize_task_manager, initialize_data
)
import state
from threading import Thread
import uvicorn

logger = logging.getLogger(__name__)


def run_server():
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000)


async def create_instance():
    config.setup_logging()
    logger.info("initialization start...")
    config.setup_CORS()
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    bank = await initialize_bank()
    characters = await initialize_characters(bank)
    state.characters = {char.name: char for char in characters}
    state.task_manager = await initialize_task_manager()
    await initialize_data()

    logger.info("Initialization complete.")

    await state.task_manager.run_queues(characters)

if __name__ == "__main__":
    asyncio.run(create_instance())
