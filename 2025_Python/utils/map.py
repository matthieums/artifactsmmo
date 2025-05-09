from data import drops
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
    return drops[item]


def find_resources(items: dict) -> dict:
    """Return a dict containing the item, its location and
    the quantity needed."""
    resource_locations = dict()

    for code, _ in items.items():
        location = find_on_map(code)
        resource_locations.update(
            {location: code}
        )
        return resource_locations
