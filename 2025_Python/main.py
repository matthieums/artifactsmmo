import asyncio
import config
import logging

from utils.initialization import initialize_bank, initialize_characters
from user_interface import load_character_tasks


logger = logging.getLogger(__name__)


async def create_instance():
    logger.info("initialization start...")
    config.setup_logging()

    bank = await initialize_bank()
    characters = await initialize_characters(bank)

    logger.info("Initialization complete.")

    logger.info("Loading user tasks...")

    load_character_tasks(characters)

    async with asyncio.TaskGroup() as tg:
        for character in characters:
            tg.create_task(character.run_tasks())

if __name__ == "__main__":
    asyncio.run(create_instance())
