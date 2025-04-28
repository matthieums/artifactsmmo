from data import lootable_from


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