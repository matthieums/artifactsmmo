from utils import get_url
import requests


class Character():
    def __init__(self, name: str) -> None:
        self.available = True
        self.name = name

    def move_to(self, location: str) -> dict:
        action = "move"
        character = self.name
        url, headers, data = get_url(character=character, action=action, location=location)
        response = requests.post(url=url, headers=headers, data=data)
        print(response.status_code)
        return response.status_code
