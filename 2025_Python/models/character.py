from utils import get_url
import requests
from decorators import check_character_position
import asyncio


class Character():
    def __init__(self, name: str, position: list) -> None:
        self.available = True
        self.position = position
        self.name = name

    async def move_to(self, location: str) -> int:
        url, headers, data = get_url(character=self.name, action="move", location=location)
        response = requests.post(url=url, headers=headers, data=data)
        json_data = response.json()
        print(f"{self.name} is moving towards {location}")
        await asyncio.sleep(json_data["data"]["cooldown"]["total_seconds"])
        print(response.status_code)
        print('move succesful')
        return response.status_code

    @check_character_position
    def fight(self, monster: str) -> int:
            url, headers = get_url(character=self.name, action="fight", location=monster)
            response = requests.post(url=url, headers=headers)
            print(f"{self.name} is fighting {monster}")
            print(response.text)
            return response.status_code


    def __repr__(self):
        return self.name
