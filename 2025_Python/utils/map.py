from __future__ import annotations
from data import drops, maps
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.character import Character


logger = logging.getLogger(__name__)


async def get_map_data(location: str):
    from utils import send_request
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


def find_closest(character: "Character", location: str) -> tuple:
    """Finds the closest location to the character's position"""
    options = maps.get(location)

    if len(options) == 1:
        return options[0]

    x, y = character.position
    min_distance = float("inf")
    closest = None

    for option in options:
        a, b = option
        distance = sum([abs(x - a), abs(y - b)])
        if distance < min_distance:
            min_distance = distance
            closest = (a, b)

    return closest
