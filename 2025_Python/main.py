from __future__ import annotations
import subprocess
import os
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


def run_react_server():
    PATH = "front-end/character-manager"
    os.chdir(PATH)

    try:
        process = subprocess.Popen(
            ["npm", "start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        for line in process.stdout:
            print(line.decode().strip())

        for line in process.stderr:
            print(f"Error: {line.decode().strip()}")

        process.wait()
        logger.info("React server started.")

    except Exception as e:
        print(f"Error starting the React server: {e}")


async def initialize():
    config.setup_logging()
    logger.info("initialization start...")

    bank = await initialize_bank()
    characters = await initialize_characters(bank)
    state.characters = {char.name: char for char in characters}

    await initialize_data()
    logger.info("Initialization complete.")

    await initialize_task_manager()


def start_server_thread():
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    return


def start_react_thread():
    react_thread = Thread(target=run_react_server)
    react_thread.daemon = True
    react_thread.start()
    return


async def create_instance():
    start_server_thread()
    await initialize()
    start_react_thread()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(create_instance())
