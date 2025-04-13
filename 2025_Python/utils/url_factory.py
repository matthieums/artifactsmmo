import config
import json
from data import locations
from typing import Optional

POST = "POST"
GET = "GET"


def get_url(character: str, action: str, location: Optional[str] = None, item: Optional[str] = None) -> tuple:
    if action == "move":
        headers = build_headers(POST)
        x, y = locations[location]
        data = {
            "x": x,
            "y": y
        }
        json_data = json.dumps(data)
        url = f"https://api.artifactsmmo.com/my/{character}/action/move"
        return url, headers, json_data

    elif action == "fight":
        headers = build_headers(POST)
        url = f"https://api.artifactsmmo.com/my/{character}/action/fight"
        return url, headers

    elif action == "rest":
        headers = build_headers(POST)
        url = f"https://api.artifactsmmo.com/my/{character}/action/rest"
        return url, headers

    elif action == "gather":
        headers = build_headers(POST)
        url = f"https://api.artifactsmmo.com/my/{character}/action/gathering"
        return url, headers

    elif action == "craft":
        headers = build_headers(POST)
        data = json.dumps({
            "code": item
        })
        url = f"https://api.artifactsmmo.com/my/{character}/action/crafting"
        return url, headers, data

def get_info_url(item):
    headers = build_headers(GET)
    url = f"https://api.artifactsmmo.com/items/{item}"
    return url, headers


def get_unequip_url(character, slot):
    headers = build_headers(POST)
    url = f"https://api.artifactsmmo.com/my/{character}/action/unequip"
    data = {
        "slot": slot
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
