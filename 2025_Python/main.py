import asyncio
from models import Character, Bank, Inventory
import config
from utils import send_request
import logging
from dateutil import parser
from tzlocal import get_localzone
from datetime import datetime
import math

######### This is where the process starts and makes calls to create the characters and distribute tasks

logger = logging.getLogger(__name__)


async def initialize_characters():
    logger.info("Initializing Characters...")
    response = await send_request(action="char_data")
    data = response.json()["data"]
    characters = [Character.from_api_data(entry) for entry in data]

    if len(characters) == 5:
        logger.info("Characters succesfully initialized")

    else:
        logger.error("Error during character initialization")
        raise

    local_tz = get_localzone()
    local_time = datetime.now(local_tz)

    logger.info("Initializing inventory...")
    logger.info("Setting cooldown values...")
    for i in range(len(characters)):
        inventory = Inventory.from_data(data[i], characters[i])
        inventory.owner = characters[i]
        characters[i].inventory = inventory
        characters[i].cooldown_expiration = parser.isoparse(data[i]["cooldown_expiration"])
        characters[i].cooldown_duration = math.ceil((characters[i].cooldown_expiration - local_time).total_seconds())
        # TODO: Add error checking
    logger.info("Inventory initialized.")
    logger.info("Setting cooldown values.")

    return characters


async def initialize_bank():
    logger.info("Initializing bank...")
    bank_data = await Bank.get_bank_details()
    bank_items = await Bank.get_bank_items()
    logger.info("Bank initialized.")
    return Bank.from_api_data(bank_data, bank_items)


async def create_instance():
    logger.info("initialization start...")
    config.setup_logging()

    characters = await initialize_characters()
    bank = await initialize_bank()

    logger.info("Initialization complete.")

    g = "gather"
    d= "deposit"
    w = "withdraw"
    f = "fight"
    cr = "craft"
    r = "rest"
    t_e = "toggle_equipped"

    c_r = "copper_rocks"
    a_w = "ash_wood"
    a_t = "ash_tree"
    ch = "chickens"
    a_p = "ash_plank"
    w_s = "wooden_shield"
    e_i = "empty_inventory"
    c_o = "copper_ore"
    g_s = "green_slime"
    co = "copper"
    i_r = "iron_rocks"

        # For individual commands
        # await asyncio.gather(
        #     run_character_loop(None, characters[0], g, location=c_r ),
        #     run_character_loop(None, characters[1], g, location=c_r ),
        #     run_character_loop(None, characters[2], g, location=c_r ),
        #     run_character_loop(None, characters[3], g, location=c_r ),
        #     run_character_loop(None, characters[4], g, location=c_r ),
        #     return_exceptions=True
        # )

    # When I need everyone to do the same thing
    async with asyncio.TaskGroup() as tg:
        for character in characters:
            if character.is_on_cooldown():
                character.build_task(1, "handle_cooldown", character.cooldown_duration)

    
            # character.build_task(1, e_i)
            # character.build_task(1, w, item=c_o, quantity=100)
            # character.build_task(1, cr, co, quantity=10)
            # character.build_task(1, e_i)
            # character.build_task(1, w, item=c_o, quantity=100)
            # character.build_task(1, cr, co, quantity=10)
            # character.build_task(1, e_i)
            # character.build_task(1, w, item=c_o, quantity=100)
            # character.build_task(1, cr, co, quantity=10)
            # character.build_task(None, cr, co)

            character.build_task(None, g, location=i_r)
            # character.build_task(None, g, location=i_r)
            # character.build_task(None, cr, co)
            # character.build_task(None, g, location=i_r)
            # character.build_task(None, cr, co)
            # character.build_task(None, e_i)

            tg.create_task(character.run_tasks())

if __name__ == "__main__":
    asyncio.run(create_instance())
