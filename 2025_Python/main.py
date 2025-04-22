import asyncio
import httpx
from models import Character, Bank
import config
from utils import get_url
import logging

######### This is where the process starts and makes calls to create the characters and distribute tasks

logger = logging.getLogger(__name__)

async def run_character_loop(iterations: int | None, character, method_name: str, *args, **kwargs):
    logger.info(f"Initializing loop for {character.name}...")
    method = getattr(character, method_name)

    if not callable(method):
        raise AttributeError(f"'{method_name} is not a valid method")

    if iterations is None:
        while True:
            logger.info(f"calling method {method_name}")
            await method(*args, **kwargs)

    elif isinstance(iterations, int):
        for _ in range(iterations):
            await method(*args, **kwargs)
    else:
        raise ValueError("Iterations must be an int or None")


async def initialize_characters():
    logging.info("Initializing characters...")
    url, headers = get_url(action="char_data")
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)
        data = response.json()["data"]
        logging.info("Characters initialized.")
        characters = [Character.from_api_data(entry) for entry in data]
        if len(characters) == 5:
            logging.info("characters succesfully initialized")
            return characters
        else:
            logging.error("Error during character initialization")
            raise


async def initialize_bank():
    logging.info("Initializing bank...")
    bank_data = await Bank.get_bank_details()
    bank_items = await Bank.get_bank_items()
    logging.info("Bank initialized.")
    return Bank.from_api_data(bank_data, bank_items)


async def create_instance():
    config.setup_logging()

    characters = await initialize_characters()
    bank = await initialize_bank()

    logging.info("initialization complete")

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
    tasks = []
    for character in characters:
        tasks.append(run_character_loop(None, character, e_i))
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(create_instance())
