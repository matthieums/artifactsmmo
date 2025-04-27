from data import lootable_from
from utils import send_request
import logging

logger = logging.getLogger(__name__)


async def get_map_data(location: str):
    action = "map_data"
    try:
        response = await send_request(action=action, location=location)
    except Exception as e:
        logger.error(f"Failed to get data for map {location}. {str(e)}")
    else:
        return response.json()


async def find_on_map(item: str) -> str:
    """Return the map location code on which to find an item"""
    return lootable_from[item]


def find_resources(items) -> list:
    """Return a dict containing the item, its location and
    the quantity needed."""
    resource_list = {}

    for item in items:
        code, qty = item["code"], item["quantity"]
        location = find_on_map(code)
        resource_list["location"] = location
        resource_list["code"] = code
        resource_list["quantity"] = qty

    return resource_list
