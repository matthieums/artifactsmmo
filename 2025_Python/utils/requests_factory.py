from typing import Optional, Any, Dict, Callable, TYPE_CHECKING
import config
import json
import httpx
import logging
import asyncio

from utils.map import find_closest
from utils.feedback import format_action_message

if TYPE_CHECKING:
    from models.character import Character

logger = logging.getLogger(__name__)
POST = "POST"
GET = "GET"
BASE_URL = "https://api.artifactsmmo.com"


async def send_request(
    character: Optional["Character"] = None,
    action: Optional[str] = None,
    location: Optional[str] = None,
    item: Optional[str] = None,
    slot: Optional[str] = None,
    quantity: Optional[int] = None
) -> tuple:

    if action not in dispatcher:
        raise KeyError("Action does not exist. Impossible request.")

    kwargs = {
        "action": action,
        "character": character,
        "location": location,
        "item": item,
        "slot": slot,
        "quantity": quantity
    }

    handler = dispatcher[action]
    try:
        response = await handler(**kwargs)
    except Exception as e:
        logger.error(f"{str(e)}")
        raise
    else:
        logger.debug("Request successful")
        format_action_message(character, action, location)

        # Special case for map_data
        if isinstance(response, list):
            return response

        if action in character_actions and response.status_code == 200:
            character.set_cooldown_expiration(
                response.json()["data"]["cooldown"]["expiration"]
            )
            logger.debug(f'Cooldown set to {response.json()["data"]["cooldown"]["expiration"]}')
        return response


async def make_post_request(
    url: str,
    headers: dict,
    data: dict | None = None
):
    kwargs = {
        "url": url,
        "headers": headers,
    }

    if data:
        kwargs["data"] = data

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(**kwargs)
        except httpx.RequestError as e:
            logging.error(f"Failed to send post request: {e}", exc_info=True)
            raise e
        else:
            return response


async def make_get_request(url: str, headers: dict, params: dict = None):
    kwargs = {
        "url": url,
        "headers": headers,
        "params": params or {}
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(**kwargs)
        except Exception as e:
            logging.error(
                f"Failed to build or send get request. \n{e}", exc_info=True
                )
            raise e
        else:
            return response


def build_headers(request: str) -> dict:
    if request == POST:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.API_KEY}"
        }
        return headers

    elif request == GET:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.API_KEY}"
        }
        return headers


async def move_action(character, location, *args, **kwargs):
    x, y = find_closest(character, location)
    headers = build_headers(POST)
    data = {
        "x": x,
        "y": y
    }
    json_data = json.dumps(data)
    url = f"{BASE_URL}/my/{character}/action/move"
    return await make_post_request(
        url=url, headers=headers, data=json_data
    )


async def map_data(character, location, *args, **kwargs):
    x, y = find_closest(character, location)
    headers = build_headers(GET)
    url = f"{BASE_URL}/maps/{x}/{y}"
    return await make_get_request(url=url, headers=headers)


async def fight_action(character, *args, **kwargs):
    headers = build_headers(POST)
    url = f"{BASE_URL}/my/{character}/action/fight"
    return await make_post_request(url=url, headers=headers)


async def rest_action(character, *args, **kwargs):
    headers = build_headers(POST)
    url = f"{BASE_URL}/my/{character}/action/rest"
    return await make_post_request(url=url, headers=headers)


async def gather_action(character, *args, **kwargs):
    headers = build_headers(POST)
    url = f"{BASE_URL}/my/{character}/action/gathering"
    return await make_post_request(url=url, headers=headers)


async def craft_action(character, item, *args, **kwargs):
    if not item:
        raise Exception("Missing argument: item")
    headers = build_headers(POST)
    json_data = json.dumps({
        "code": item
    })
    url = f"{BASE_URL}/my/{character}/action/crafting"
    return await make_post_request(
        url=url, headers=headers, data=json_data
    )


async def equip_action(character, action, item, slot, *args, **kwargs):
    headers = build_headers(POST)
    url = f"{BASE_URL}/my/{character}/action/{action}"
    data = {
        "code": item,
        "slot": slot
    }
    json_data = json.dumps(data, *args, **kwargs)
    return await make_post_request(
        url=url, headers=headers, data=json_data
    )


async def bank_action(character, action, item, quantity, *args, **kwargs):
    headers = build_headers(POST)
    url = f"{BASE_URL}/my/{character}/action/bank/{action}"
    data = {
        "code": item,
        "quantity": quantity
    }
    json_data = json.dumps(data)
    return await make_post_request(
        url=url, headers=headers, data=json_data
    )


async def item_info(item, *args, **kwargs):
    headers = build_headers(GET)
    url = f"{BASE_URL}/items/{item}"
    return await make_get_request(url=url, headers=headers)


async def get_characters(*args, **kwargs):
    headers = build_headers(GET)
    url = f"{BASE_URL}/my/characters"
    return await make_get_request(url=url, headers=headers)


async def bank_details(*args, **kwargs):
    headers = build_headers(GET)
    url = f"{BASE_URL}/my/bank"
    return await make_get_request(url=url, headers=headers)


async def bank_items(*args, **kwargs):
    headers = build_headers(GET)
    url = f"{BASE_URL}/my/bank/items"
    return await make_get_request(url=url, headers=headers)


async def get_all_monsters(*args, **kwargs):
    headers = build_headers(GET)
    url = f"{BASE_URL}/monsters"
    params = {"size": 100}
    return await make_get_request(
        url=url, headers=headers, params=params
    )


async def get_all_resources(*args, **kwargs):
    headers = build_headers(GET)
    url = f"{BASE_URL}/resources"
    params = {"size": 100}
    return await make_get_request(
        url=url, headers=headers, params=params
    )


async def get_all_maps(*args, **kwargs):
    headers = build_headers(GET)
    url = f"{BASE_URL}/maps"

    async def _fetch_page(page_number):
        params = {"page": page_number, "size": 100}
        return await make_get_request(url=url, headers=headers, params=params)

    responses = await asyncio.gather(*(_fetch_page(i) for i in range(1, 5)))
    return responses


dispatcher: Dict[str, Callable[..., Any]] = {
    "move": move_action,
    "fight": fight_action,
    "rest": rest_action,
    "gather": gather_action,
    "craft": craft_action,
    "equip": equip_action,
    "unequip": equip_action,
    "char_data": get_characters,
    "withdraw": bank_action,
    "empty": bank_action,
    "deposit": bank_action,
    "bank_details": bank_details,
    "item_info": item_info,
    "bank_items": bank_items,
    "get_all_monsters": get_all_monsters,
    "get_all_resources": get_all_resources,
    "get_all_maps": get_all_maps,
    "map_data": map_data,
}


character_actions = {
    "move",
    "fight",
    "rest",
    "gather",
    "craft",
    "equip",
    "unequip",
    "withdraw",
    "empty",
    "deposit",
}