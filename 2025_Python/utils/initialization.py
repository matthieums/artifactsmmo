from __future__ import annotations
import logging
from dateutil import parser
from tzlocal import get_localzone
from datetime import datetime
import math

from data.monsters import monsters
from data.resources import resources
from data.drops import drops
from models.bank import Bank
from models import Character
from utils.requests_factory import send_request
from models.task_manager import TaskManager
from user_interface import load_character_tasks

logger = logging.getLogger(__name__)
NUMBER_OF_CHARACTERS = 5


async def initialize_characters(bank):
    logger.info("Initializing Characters...")

    try:
        response = await send_request(action="char_data")
    except Exception as e:
        logger.error(f"Failed to initialize characters: {e}")
        raise
    else:
        local_tz = get_localzone()
        local_time = datetime.now(local_tz)
        data = response.json()["data"]
        characters = [Character.from_api_data(entry, bank) for entry in data]

        assert len(characters) == NUMBER_OF_CHARACTERS
        logger.info("Characters succesfully initialized")

        for i in range(len(characters)):
            logging.debug(
                f"{characters[i]}'s inventory initialized with: "
                f"{characters[i].inventory}"
            )
            logging.debug(
                f"{characters[i]}'s equipment initialized with: "
                f"{characters[i].equipment}"
            )

            logger.info("Setting cooldown values...")
            characters[i].cooldown_expiration = parser.isoparse(
                data[i]["cooldown_expiration"]
                )
            characters[i].cooldown_duration = math.ceil(
                (characters[i].cooldown_expiration - local_time)
                .total_seconds()
            )
            logger.debug(
                "Coolodown duration initialized to "
                f"{characters[i].cooldown_duration}"
            )

        return characters


async def initialize_bank():
    logger.info("Initializing bank...")
    try:
        bank_data = await Bank.get_bank_details()
        bank_items = await Bank.get_bank_items()
    except Exception as e:
        logger.error(f"Failed to initialize bank: {e}")
        raise
    else:
        bank = Bank.from_api_data(bank_data, bank_items)
        logger.debug(f"Bank initialized with {repr(bank)}")
        return bank


async def initialize_task_manager():
    logger.info("Initializing task manager")

    task_manager = TaskManager()
    load_character_tasks(task_manager)

    logger.info("Task manager initialized")
    return task_manager


async def initialize_data():
    logger.info("Initialiazing data...")

    response = await send_request(action="get_all_monsters")
    monster_data = response.json()["data"]
    response = await send_request(action="get_all_resources")
    resources_data = response.json()["data"]

    monsters.update(monster["code"] for monster in monster_data)
    resources.update(resource["code"] for resource in resources_data)
    drops.update({
            drop["code"]: entity["code"]
            for entity in monster_data + resources_data
            for drop in entity["drops"]
        })

    logger.info("Data initialized...")
    return
