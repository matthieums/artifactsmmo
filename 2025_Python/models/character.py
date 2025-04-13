from utils import get_url
import requests
from decorators import check_character_position
import asyncio
from data import locations
from typing import Optional
import httpx


class Character():
    def __init__(self, name: str, position: list, equipment: dict, inventory: dict) -> None:
        self.available = True
        self.position = position
        self.name = name
        self.equipment = equipment
        self.inventory = inventory

    @staticmethod
    async def handle_cooldown(data: dict) -> None:
        json_data = data.json()
        cooldown = json_data["data"]["cooldown"]["total_seconds"]
        remaining = cooldown + 1

        while remaining > 0:
            print(f"Cooldown remaining: {remaining} seconds")
            sleep_time = min(5, remaining)
            await asyncio.sleep(sleep_time)
            remaining -= sleep_time
        return

    @staticmethod
    async def get_information_about(item: str) -> dict:
        url, headers = get_url(action="info", item=item)
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)
        print(response.text)
        return response.json()

    async def move_to(self, location: str) -> int:
        url, headers, data = get_url(character=self.name, action="move", location=location)
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
        print(f"{self.name} has moved to {location}...")
        await self.handle_cooldown(response)
        return response.status_code

    @check_character_position
    async def fight(self, location: str) -> int:
        url, headers = get_url(character=self.name, action="fight", location=location)
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers)
        print(f"{self.name} has fought {location}")
        await self.handle_cooldown(response)
        print(response.text)
        return response.status_code

    async def rest(self):
        url, headers = get_url(character=self.name, action="rest")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers)
        print(f"{self.name} has rested")
        await self.handle_cooldown(response)
        print(response.text)
        return response.status_code

    @check_character_position
    async def gather(self, location: str) -> int:
        url, headers = get_url(character=self.name, action="gather")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers)
            print(response.text)
            print(f"{self.name} has gathered from {location}")
            await self.handle_cooldown(response)
            return response.status_code

    def has_equipped(self, item: str):
        return item in self.equipment.values()

    async def toggle_equiped(self, item: str) -> int:
        # TODO: Check if already unequipped
        item_data = await self.get_information_about(item)
        slot = item_data["data"]["type"]

        if self.has_equipped(item):
            action = "unequip"
        else:
            action = "equip"

        url, headers, data = get_url(character=self.name, action=action, item=item, slot=slot)
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
        print(response.text)
        await self.handle_cooldown(response)
        return response.status_code     

    async def craft(self, item: str) -> int:
        item_data = await self.get_information_about(item)
        print(item_data)
        skill = item_data["data"]["craft"]["skill"]
        if not self.position == locations[skill]:
            await self.move_to(skill)

        url, headers, data = get_url(character=self.name, action="craft", item=item)
        response = requests.post(url=url, headers=headers, data=data)
        print(response.text)
        await self.handle_cooldown(response)
        return response.status_code

        # used to craft it
            # if enough resources:
                # await move to appropriate station
                # craft item
            # else:
                # Check necessary resources
                # gather resources

    @check_character_position
    async def deposit(self, quantity: int, item: str) -> int:
        if item not in self.inventory:
            return 0

        deposit_amount = self.inventory[item] - quantity

        url, headers, data = get_url(character=self.name, item=item, quantity=deposit_amount, action="deposit")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
        print(f"{self.name} has deposited {deposit_amount} {item}")
        await self.handle_cooldown(response)
        return response.status_code

    @check_character_position
    async def withdraw(self, quantity: Optional[int], item: str) -> int:
        url, headers, data = get_url(character=self.name, item=item, quantity=quantity, action="withdraw")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
        print(response.text)
        print(f"{self.name} has withdrawn {quantity} {item}")
        await self.handle_cooldown(response)
        return response.status_code

    def __repr__(self):
        return self.name
