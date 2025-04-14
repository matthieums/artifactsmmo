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

    @classmethod
    def from_api_data(cls, data: dict) -> "Character":
        slot_keys = [
            "weapon_slot", "shield_slot", "helmet_slot", "body_armor_slot",
            "leg_armor_slot", "boots_slot", "ring1_slot", "ring2_slot",
            "amulet_slot", "artifact1_slot", "artifact2_slot", "artifact3_slot"
        ]

        return cls(
            name=data.get("name"),
            position=[data.get("x"), data.get("y")],
            equipment={slot: data.get(slot, "") for slot in slot_keys },
            inventory={item["code"]: item["quantity"] for item in data["inventory"] if item["quantity"] > 0}
        )

    @staticmethod
    async def handle_cooldown(data: dict) -> None:
        json_data = data.json()
        cooldown = json_data["data"]["cooldown"]["total_seconds"]
        remaining = cooldown

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
            self.update_position(location)
            await self.handle_cooldown(response)
            return response.status_code

    def update_position(self, location):
        self.position = locations[location]


    @check_character_position
    async def fight(self, location: str) -> int:
        url, headers = get_url(character=self.name, action="fight", location=location)
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers)
        print(f"{self.name} has fought {location}")
        await self.handle_cooldown(response)
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
            print(f"{self.name} has gathered from {location}")
            await self.handle_cooldown(response)
            return response.status_code

    def has_equipped(self, item: str):
        return item in self.equipment.values()

    async def toggle_equipped(self, item: str) -> int:
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
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
            print(response.text)
            await self.handle_cooldown(response)
            return response.status_code

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
