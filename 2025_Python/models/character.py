from utils import get_url
from data import locations
import requests


class Character():
    def __init__(self, name: str, position: list) -> None:
        self.available = True
        self.position = position
        self.name = name

    def move_to(self, location: str) -> int:
        url, headers, data = get_url(character=self.name, action="move", location=location)
        response = requests.post(url=url, headers=headers, data=data)
        print(response.text)
        return response.status_code

    def fight(self, monster: str) -> int:
        if not self.position:
            return False

        if self.position == locations[monster]:
            url, headers = get_url(character=self.name, action="fight", location=monster)
            response = requests.post(url=url, headers=headers)
            print(response.text)
            return response.status_code

        else:
            self.move_to(monster)
            # WAIT FOR ARRIVAL
            # FIGHT
