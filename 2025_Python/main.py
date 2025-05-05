from __future__ import annotations
import asyncio
import config
import logging
from utils.initialization import initialize_bank, initialize_characters, initialize_task_manager

logger = logging.getLogger(__name__)


async def create_instance():
    logger.info("initialization start...")
    config.setup_logging()

    bank = await initialize_bank()
    characters = await initialize_characters(bank)
    task_manager = await initialize_task_manager(characters)

    logger.info("Initialization complete.")

    await task_manager.run_queues(characters)

if __name__ == "__main__":
    asyncio.run(create_instance())
