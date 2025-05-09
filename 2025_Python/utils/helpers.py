from data import lootable_from, monsters, resources
import logging

logger = logging.getLogger(__name__)


def subtract_dicts(dict1, dict2):
    for key, value in dict(dict1).items():
        available_qty = dict2.get(key, 0)

        if available_qty == "inf":
            del dict1[key]
            continue

        value -= available_qty

        if value <= 0:
            del dict1[key]
        else:
            dict1[key] = value
    return dict1


async def find_on_map(item: str) -> str:
    """Return the map location code on which to find an item"""
    return lootable_from[item]


def determine_action(location: str) -> str:
    if location in monsters:
        logger.debug("Resource found in Monsters")
        return "fight"
    elif location in resources:
        logger.debug("Resource found in locations")
        return "gather"
    else:
        logger.error("Resource not found")
        raise ValueError("The location is neither a monster nor a resource")
