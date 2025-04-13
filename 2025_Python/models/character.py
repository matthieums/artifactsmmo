from utils import get_url
import requests
from decorators import check_character_position
import asyncio


class Character():
    def __init__(self, name: str, position: list) -> None:
        self.available = True
        self.position = position
        self.name = name

    @staticmethod
    async def handle_cooldown(data):
        cooldown = data["data"]["cooldown"]["total_seconds"]
        remaining = cooldown

        while remaining > 0:
            print(f"Cooldown remaining: {remaining} seconds")
            sleep_time = min(5, remaining)
            await asyncio.sleep(sleep_time)
            remaining -= sleep_time

        print("Ready for next action!")
        return

    async def move_to(self, location: str) -> int:
        url, headers, data = get_url(character=self.name, action="move", location=location)
        response = requests.post(url=url, headers=headers, data=data)
        json_data = response.json()
        json_data = response.json()
        print(f"{self.name} has moved to {location}...")
        await self.handle_cooldown(json_data)
        print(response.status_code)
        print('move succesful')
        return response.status_code

    @check_character_position
    async def fight(self, monster: str) -> int:
            url, headers = get_url(character=self.name, action="fight", location=monster)
            response = requests.post(url=url, headers=headers)
            print(f"{self.name} has fought {monster}")
            json_data = response.json()
            await self.handle_cooldown(json_data)
            print(response.text)
            return response.status_code

    async def rest(self):
        url, headers = get_url(character=self.name, action="rest")
        response = requests.post(url=url, headers=headers)
        print(f"{self.name} has rested")
        json_data = response.json()
        await self.handle_cooldown(json_data)
        print(response.text)
        return response.status_code

    def __repr__(self):
        return self.name
