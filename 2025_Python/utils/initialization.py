from models import Character, Bank, Inventory
from utils.requests_factory import send_request
import logging
from dateutil import parser
from tzlocal import get_localzone
from datetime import datetime
import math

logger = logging.getLogger(__name__)
NUMBER_OF_CHARACTERS = 5


async def initialize_characters(bank):
    logger.info("Initializing Characters...")
    try:
        response = await send_request(action="char_data")
    except Exception as e:
        logger.error(f"Failed to initialize characters: {e}")
        raise
    data = response.json()["data"]
    characters = [Character.from_api_data(entry) for entry in data]

    assert len(characters) == NUMBER_OF_CHARACTERS
    logger.info("Characters succesfully initialized")

    local_tz = get_localzone()
    local_time = datetime.now(local_tz)

    logger.info("Initializing inventory...")
    logger.info("Setting cooldown values...")
    for i in range(len(characters)):
        characters[i].bank = bank
        inventory = Inventory.from_data(data[i], characters[i])
        inventory.owner = characters[i]
        characters[i].inventory = inventory
        characters[i].cooldown_expiration = parser.isoparse(data[i]["cooldown_expiration"])
        characters[i].cooldown_duration = math.ceil((characters[i].cooldown_expiration - local_time).total_seconds())
    logger.info("Inventory initialized.")
    logger.info("Setting cooldown values.")

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
        logger.info("Bank initialized.")
        return Bank.from_api_data(bank_data, bank_items)
