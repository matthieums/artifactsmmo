import config
import json
from data import locations
from typing import Optional

POST = "POST"
GET = "GET"
BASE_URL = "https://api.artifactsmmo.com"


def get_url(
        character: Optional[str] = None, action: Optional[str] = None,
        location: Optional[str] = None, item: Optional[str] = None,
        slot: Optional[str] = None, quantity: Optional[int] = None
        ) -> tuple:

    if action == "move":
        headers = build_headers(POST)
        x, y = locations[location]
        data = {
            "x": x,
            "y": y
        }
        json_data = json.dumps(data)
        url = f"{BASE_URL}/my/{character}/action/move"
        return url, headers, json_data

    elif action == "fight":
        headers = build_headers(POST)
        url = f"{BASE_URL}/my/{character}/action/fight"
        return url, headers

    elif action == "rest":
        headers = build_headers(POST)
        url = f"{BASE_URL}/my/{character}/action/rest"
        return url, headers

    elif action == "gather":
        headers = build_headers(POST)
        url = f"{BASE_URL}/my/{character}/action/gathering"
        return url, headers

    elif action == "craft":
        headers = build_headers(POST)
        data = json.dumps({
            "code": item
        })
        url = f"{BASE_URL}/my/{character}/action/crafting"
        return url, headers, data

    elif action in ["equip", "unequip"]:
        headers = build_headers(POST)
        url = f"{BASE_URL}/my/{character}/action/{action}"
        data = {
            "code": item,
            "slot": slot
        }
        json_data = json.dumps(data)
        return url, headers, json_data

    elif action == "info":
        headers = build_headers(GET)
        url = f"{BASE_URL}/items/{item}"
        return url, headers

    elif action in ["withdraw", "deposit"]:
        headers = build_headers(POST)
        url = f"{BASE_URL}/my/{character}/action/bank/{action}"
        data = {
            "code": item,
            "quantity": quantity
        }
        json_data = json.dumps(data)
        return url, headers, json_data


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
