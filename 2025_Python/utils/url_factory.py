import config
import json
from data import locations

POST = "POST"

def get_url(character: str, action: str, location: str) -> tuple:
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

    else:
        pass


def build_headers(request: str) -> dict:
    if request == POST:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.API_KEY}"
        }
        return headers

    elif request == 'GET':
        pass
