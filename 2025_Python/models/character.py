from utils import get_url
import requests
from decorators import check_character_position
import asyncio
from data import locations, SLOT_KEYS, XP_KEYS, HP_KEYS, COMBAT_KEYS
from typing import Optional
import httpx


class Character():
    def __init__(
        self,
        name: str,
        hp: dict,
        levels: dict,
        gold: int,
        position: list,
        equipment: dict,
        inventory: dict,
        max_items: int,
        combat: dict
    ) -> None:
        self.name = name
        self.hp = hp
        self.levels = levels
        self.gold = gold
        self.position = position
        self.equipment = equipment
        self.inventory = inventory
        self.max_items = max_items
        self.combat = combat
        self.available = True

    @classmethod
    def from_api_data(cls, data: dict) -> "Character":
        return cls(
            name=data.get("name"),
            gold=data.get("gold"),
            levels={key: data.get(key) for key in XP_KEYS},
            position=[data.get("x"), data.get("y")],
            hp={stat: data.get(stat) for stat in HP_KEYS},
            equipment={slot: data.get(slot, "") for slot in SLOT_KEYS},
            inventory={item["code"]: item["quantity"] for item in data.get("inventory", []) if item["quantity"] > 0},
            max_items=data.get("inventory_max_items"),
            combat={stat: data.get(stat) for stat in COMBAT_KEYS}
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

    @staticmethod
    def detect_error(response):
        return response.status_code != 200

    @staticmethod
    def generate_error_message(response, name, action, location):
        error_detail = response.text
        print(f"{name} failed to perform {action} at {location}."
              f"{error_detail}")
        return 1

    @staticmethod
    def generate_success_message(name, action, location):
        print(f"{name} has {action}ed at {location}")
        return 1

    def hp_diff(self, previous, current):
        return previous - current

    def update_gold(self, action, quantity):
        if action == "gain":
            self.gold += quantity
            print(f"{quantity} gold added to {self.name}")
        elif action == "lose":
            self.gold -= quantity
            print(f"{quantity} gold removed from {self.name}")

    def update_hp(self, value):
        hp_difference = self.hp_diff(self.hp["hp"], value)
        if hp_difference > 0:
            print(f"{self.name} lost {hp_difference} hp")
        elif hp_difference < 0:
            print(f"{self.name} gained {hp_difference} hp")
        else:
            print("no hp gain nor loss")

    def handle_fight_data(self, response):
        data = response["data"]["fight"]
        print(f"{self.name} {data['result']}")
        if data["gold"]:
            self.update_gold("gain", data["gold"])
            print(f"{data['gold']} gold received")
        for item in data["drops"]:
            self.update_inventory("looted", item, data["drops"][item])
        self.update_hp(response["data"]["character"]["hp"])
        return 1

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
        LOW_HP_THRESHOLD = 0.2
        if self.hp["hp"] < (LOW_HP_THRESHOLD * self.hp["max_hp"]):
            await self.rest()
        url, headers = get_url(character=self.name, action="fight", location=location)
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers)
            print(f"{self.name} has fought {location}")
            self.handle_fight_data(response.json())
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
        action = "gather"
        url, headers = get_url(character=self.name, action=action)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, headers=headers)
                if self.detect_error(response):
                    self.generate_error_message(response, self.name, action, location)
                    await self.handle_cooldown(response)
                    return 0
                else:
                    self.generate_success_message(self.name, action, location)
                    await self.handle_cooldown(response)
                    return 1

        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {action}."
                  f"{exc.request.url!r}: {str(exc)}")
            return 0

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

    def update_inventory(self, action: str, item: str, value: int):
        if action in ["deposit", "empty_inventory"]:
            self.inventory[item] -= value
            if value <= 0:
                del self.inventory[item]
            print(f"{value} {item} removed from {self.name}'s inventory")
        elif action in ["looted", "withdraw"]:
            self.inventory[item] = self.inventory.get(item, 0) + value
            print(f"{value} {item} added to {self.name} inventory")
        else:
            print("action need to be added to update inventory")

    @check_character_position
    async def empty_inventory(self, keep: list = None):
        action = "empty_inventory"
        async with httpx.AsyncClient() as client:
            for item in self.inventory:
                if keep and item in keep:
                    continue
                url, headers, data = get_url(character=self.name, item=item, quantity=self.inventory[item], action="deposit")
                response = await client.post(url=url, headers=headers, data=data)
                if response.status_code == 200:
                    print(f"{self.name} has deposited {self.inventory[item]} {item}")
                    self.update_inventory(action, item, self.inventory[item])
                    await self.handle_cooldown(response)
        return

    @check_character_position
    async def deposit(self, quantity: int = None, item: str = None) -> int:
        action = "deposit"
        if item not in self.inventory:
            print(f"There is no {item} to deposit")
            return 0

        deposit_amount = quantity if quantity else self.inventory[item]

        if deposit_amount > self.inventory[item]:
            deposit_amount = self.inventory[item]

        url, headers, data = get_url(character=self.name, item=item, quantity=deposit_amount, action="deposit")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
            if response.status_code == 200:
                self.update_inventory(action, item, deposit_amount)
                await self.handle_cooldown(response)
                return response.status_code
            print("error during deposit")

    @check_character_position
    async def withdraw(self, quantity: Optional[int], item: str) -> int:
        action = "withdraw"
        url, headers, data = get_url(character=self.name, item=item, quantity=quantity, action=action)
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
        self.update_inventory(action, item, quantity)
        await self.handle_cooldown(response)
        return response.status_code

    def __repr__(self):
        return self.name
