from __future__ import annotations
import os
import asyncio
import config
from uvicorn import Config, Server
import logging
from utils.initialization import (
    initialize_bank, initialize_characters,
    initialize_task_manager, initialize_data
)
import state

logger = logging.getLogger(__name__)


async def start_app_server():
    config = Config(
        "api.server:app", host="127.0.0.1", port=8000, log_level="info"
    )
    await Server(config).serve()


async def start_react_server():
    PATH = "front-end/character-manager"
    os.chdir(PATH)

    process = await asyncio.create_subprocess_exec(
        "npm", "start",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async def log_stream(stream, is_error=False):
        while True:
            line = await stream.readline()
            if not line:
                break
            decoded = line.decode().strip()
            if is_error:
                logger.error(f"React: {decoded}")
            else:
                logger.info(f"React: {decoded}")

    await asyncio.gather(
        log_stream(process.stdout),
        log_stream(process.stderr, is_error=True),
    )
    await process.wait()
    logger.info("React server started.")


async def initialize():
    config.setup_logging()
    logger.info("initialization start...")

    bank = await initialize_bank()
    characters = await initialize_characters(bank)
    state.characters = {char.name: char for char in characters}

    await asyncio.gather(initialize_data(), initialize_task_manager())
    logger.info("Initialization complete.")


async def create_instance():
    await initialize()
    await asyncio.gather(start_app_server(), start_react_server())

if __name__ == "__main__":
    asyncio.run(create_instance())
