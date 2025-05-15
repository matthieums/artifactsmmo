from __future__ import annotations
import logging
import itertools
import asyncio
import state

from data.monsters import monsters
from data.resources import resources
from data.drops import drops
from data.maps import maps
from models.bank import Bank
from models import Character
from utils.requests_factory import send_request
from models.task_manager import TaskManager
# from user_interface import load_character_tasks

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
        data = response.json()["data"]
        characters = await asyncio.gather(*(
            Character.from_api_data(entry, bank)
            for entry in data
        ))
        logger.info("Characters initialized")

        return characters


async def initialize_bank():
    logger.info("Initializing bank...")
    try:
        bank_data, bank_items = await asyncio.gather(
            Bank.get_bank_details(),
            Bank.get_bank_items()
        )
    except Exception as e:
        logger.error(f"Failed to initialize bank: {e}")
        raise
    else:
        bank = Bank.from_api_data(bank_data, bank_items)
        logger.info("Bank initialized")
        return bank


async def initialize_task_manager():
    logger.info("Initializing task manager...")
    task_manager = TaskManager()
    state.task_manager = task_manager
    # load_character_tasks(task_manager)
    asyncio.create_task(state.task_manager.listen())


async def initialize_data():
    async def _init_monster_data():
        response = await send_request(action="get_all_monsters")
        monster_data = response.json()["data"]
        return monster_data

    async def _init_resources_data():
        response = await send_request(action="get_all_resources")
        resources_data = response.json()["data"]
        return resources_data

    async def _init_map_data():
        """Sends a request to get a list of responses containing all pages
        of map data and joins them into one list."""
        responses = await send_request(action="get_all_maps")
        maps_data = list(
            itertools.chain.from_iterable(
                response.json()["data"]for response in responses
                )
            )
        logger.debug(f"NUMBER OF MAPS: {len(maps_data)}")
        return maps_data
    logger.info("Initialiazing data...")

    monster_data, resources_data, maps_data = await asyncio.gather(
        _init_monster_data(), _init_resources_data(), _init_map_data()
    )

    monsters.update(monster["code"] for monster in monster_data)
    resources.update(resource["code"] for resource in resources_data)

    for map in maps_data:
        content = map.get("content")
        if content:
            code = content.get("code")
            coords = (map.get("x"), map.get("y"))
            maps[code].append(coords)

    drops.update({
        drop["code"]: entity["code"]
        for entity in monster_data + resources_data
        for drop in entity.get("drops", [])
    })

    logger.info("Data initialized...")
    return
