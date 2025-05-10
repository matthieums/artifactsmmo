
from utils.information import get_map_info, get_monster_info
from utils.helpers import find_on_map
from models import Monster, Resource
import logging

logger = logging.getLogger(__name__)


async def find_resources(items: dict) -> list[dict[str, object]]:
    """Return a list containing each item with their location"""
    resource_locations = list()

    for code in items:
        location = find_on_map(code)
        map_data = await get_map_info(location)

        type = map_data["data"]["content"]["type"]
        if type == "monster":
            monster_data = await get_monster_info(location)
            entity = Monster.from_data(map_data, monster_data)
        elif type == "resource":
            entity = Resource.from_data(map_data)
        else:
            logger.error("Wrong type ")
            raise TypeError("The requested map's type is not valid for the find_resources method.")

        resource_locations.append({code: entity})
        return resource_locations
