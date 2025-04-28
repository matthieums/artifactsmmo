from utils.requests_factory import send_request
import logging

logger = logging.getLogger(__name__)


async def get_item_info(item: str) -> dict:
    action = "item_info"
    response = await send_request(action=action, item=item)
    return response.json()


async def get_map_info(location: str):
    action = "map_data"
    response = await send_request(action=action, location=location)
    return response.json()


async def get_monster_info(location: str) -> dict:
    action = "monster_info"
    response = await send_request(action=action, location=location)
    return response.json()
