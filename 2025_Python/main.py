from __future__ import annotations
import asyncio
import config
import logging
from utils.initialization import initialize_bank, initialize_characters, initialize_task_manager
import state

logger = logging.getLogger(__name__)


async def create_instance():
    logger.info("initialization start...")
    config.setup_logging()

    bank = await initialize_bank()
    characters = await initialize_characters(bank)
    state.characters = characters
    task_manager = await initialize_task_manager()
    await initialize_data()

    logger.info("Initialization complete.")

    await task_manager.run_queues(characters)

if __name__ == "__main__":
    asyncio.run(create_instance())
