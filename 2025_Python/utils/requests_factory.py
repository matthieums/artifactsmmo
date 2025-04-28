import config
import json
from data import locations
from typing import Optional
import httpx
from utils.feedback import format_action_message
import logging

logger = logging.getLogger(__name__)

POST = "POST"
GET = "GET"
BASE_URL = "https://api.artifactsmmo.com"


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


async def make_get_request(url: str, headers: dict):
    kwargs = {
        "url": url,
        "headers": headers,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(**kwargs)
        except Exception as e:
            logging.error(f"Failed to build or send get request. \n{e}", exc_info=True)
            raise e
        else:
            return response


async def send_request(
    character: Optional[str] = None, action: Optional[str] = None,
    location: Optional[str] = None, item: Optional[str] = None,
    slot: Optional[str] = None, quantity: Optional[int] = None
) -> tuple:

    if action in ["move", "map_data"]:
        x, y = locations[location]

        if action == "move":
            headers = build_headers(POST)
            data = {
                "x": x,
                "y": y
            }
            json_data = json.dumps(data)
            url = f"{BASE_URL}/my/{character}/action/move"
            response = await make_post_request(url=url, headers=headers, data=json_data)

        elif action == "map_data":
            headers = build_headers(GET)
            url = f"{BASE_URL}/maps/{x}/{y}"
            response = await make_get_request(url=url, headers=headers)

    elif action == "fight":
        headers = build_headers(POST)
        url = f"{BASE_URL}/my/{character}/action/fight"
        response = await make_post_request(url=url, headers=headers)

    elif action == "rest":
        headers = build_headers(POST)
        url = f"{BASE_URL}/my/{character}/action/rest"
        response = await make_post_request(url=url, headers=headers)

    elif action == "gather":
        headers = build_headers(POST)
        url = f"{BASE_URL}/my/{character}/action/gathering"
        response = await make_post_request(url=url, headers=headers)

    elif action == "craft":
        if not item:
            raise Exception("Missing argument: item")
        headers = build_headers(POST)
        json_data = json.dumps({
            "code": item
        })
        url = f"{BASE_URL}/my/{character}/action/crafting"
        response = await make_post_request(url=url, headers=headers, data=json_data)

    elif action in ["equip", "unequip"]:
        headers = build_headers(POST)
        url = f"{BASE_URL}/my/{character}/action/{action}"
        data = {
            "code": item,
            "slot": slot
        }
        json_data = json.dumps(data)
        response = await make_post_request(url=url, headers=headers, data=json_data)

    elif action == "item_info":
        headers = build_headers(GET)
        url = f"{BASE_URL}/items/{item}"
        response = await make_get_request(url=url, headers=headers)
        return response

    elif action in ["withdraw", "deposit", "empty_inventory"]:
        headers = build_headers(POST)
        url = f"{BASE_URL}/my/{character}/action/bank/{action}"
        data = {
            "code": item,
            "quantity": quantity
        }
        json_data = json.dumps(data)
        response = await make_post_request(url=url, headers=headers, data=json_data)

    elif action == "char_data":
        headers = build_headers(GET)
        url = f"{BASE_URL}/my/characters"
        response = await make_get_request(url=url, headers=headers)

    elif action == "bank_details":
        headers = build_headers(GET)
        url = f"{BASE_URL}/my/bank"
        response = await make_get_request(url=url, headers=headers)

    elif action == "bank_items":
        headers = build_headers(GET)
        url = f"{BASE_URL}/my/bank/items"
        response = await make_get_request(url=url, headers=headers)

    elif action == "monster_data":
        headers = build_headers(GET)
        url = f"{BASE_URL}/monsters/get"
        data = {
            "code": location,
        }
        json_data = json.dumps(data)
        response = await make_get_request(url=url, headers=headers, data=data)

    if response.is_success:
        format_action_message(character, action, location)

    return response


def build_headers(request: str) -> dict:
    if request == POST:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.API_KEY}"
        }
        return headers

    elif request == 'GET':
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.API_KEY}"
        }
        return headers
