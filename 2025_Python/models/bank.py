# How to update the bank during the script? I mean you could just destroy the bank
# and recreate it based on the fetched data.

from utils import send_request
import logging
from models import ItemContainer, Item
from collections import defaultdict
import asyncio
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models import Character

logger = logging.getLogger(__name__)


class Bank(ItemContainer):
    name_of_gather = "withdraw"

    def __init__(self, slots: dict, gold: int, inventory):
        self.slots = slots
        self.gold = gold
        self.inventory = inventory
        self.reserved = defaultdict(dict)
        self.lock = asyncio.Lock()

    @classmethod
    def from_api_data(cls, details, items) -> "Bank":
        slots = details.get("slots")
        gold = details.get("gold")

        if not slots or not gold:
            raise ValueError("Missing required fields: 'slots' or 'gold'.")

        inventory = {
            item["code"]: item["quantity"] for item in items
        }
        return cls(slots=slots, gold=gold, inventory=inventory)

    @classmethod
    async def get_bank_details(cls):

        response = response = await send_request(action="bank_details")
        data = response.json()["data"]
        if response.is_success:
            data = response.json()["data"]
            return data
        else:
            raise Exception("Problem during bank initialization")

    @classmethod
    async def get_bank_items(cls):
        response = await send_request(action="bank_items")
        if response.is_success:
            data = response.json()["data"]
            return data
        else:
            raise Exception("Problem during bank initialization")

    async def deposit(self, character: Character, item: str, quantity: int) -> int:
        action = "deposit"
        available = character.inventory.get(item)

        if available is None:
            logger.error(f"There is no {item} to deposit")
            return 0

        if quantity and quantity <= available:
            deposit_amount = quantity
        else:
            deposit_amount = available

        try:
            response = await send_request(
                character=character,
                item=item,
                quantity=quantity,
                action=action
            )
        except Exception as e:
            logger.error(f"Error while trying to deposit: {str(e)}")
        else:
            async with self.lock:
                self.add(item, quantity)
            character.inventory.remove(item, deposit_amount)
            data = response.json()
            await character.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
            return 1

    async def withdraw(self, character: Character, item: str, quantity: int) -> int:
        action = "withdraw"

        free_space = character.inventory.free_space()
        if quantity and quantity <= free_space:
            withdraw_amount = quantity
        else:
            withdraw_amount = free_space
            print(f"{character} can only withdraw {free_space} at the moment")
        try:
            response = await send_request(
                character=character,
                item=item,
                quantity=withdraw_amount,
                action=action
            )
        except Exception as e:
            logger.error(f"Error while trying to deposit: {str(e)}")
        else:
            async with self.lock:
                self.remove(item, quantity)
            data = response.json()
            print(f"{character} withdrew {withdraw_amount} {item}")
            await character.handle_cooldown(data["data"]["cooldown"]["total_seconds"])

    def remove(self, item, quantity):
        inventory = self.inventory
        if item not in inventory:
            raise ValueError(
                f"No {item} found in bank's inventory. Cannot remove."
                )

        inventory[item] -= quantity
        print(f"{quantity} {item} removed from bank's inventory")

        if inventory[item] <= 0:
            del inventory[item]
            print(f"No more {item} in {self.owner}'s inventory")
        return 1

    def add(self, item: str, quantity: int) -> int:
        self.inventory[item] += quantity
        return 1

    def available(self, items: dict) -> dict:
        """Returns a dictionary of the available items found
        in the bank {code: qty}"""
        available = {}
        for code, qty in items.items():
            if self.inventory.get(code, 0) >= qty:
                available[code] = qty
        return available

    async def reserve(self, booker: Character, items):
        for code, quantity in items.items():
            self.reserved[booker].update({code: quantity})
            self.inventory[code] -= quantity
            # reserved = {character: [{item1: qty}, {item2: qty}]}
        return

    async def clear_reservation(self, booker: Character, item):
        logger.debug("Clearing reservation")
        del self.reserved[booker][item]
        return

    def get(self, item: str | Item) -> dict:
        code = item if not item.isinstance(Item) else item.code

        quantity = self.inventory.get(code, 0)

        return quantity

    def available(self, items: dict) -> dict:
        """Returns a dictionary of the available items found
        in the bank {code: qty}"""
        return {code: self.inventory.get(code, 0) for code in items}

    def __str__(self):
        return "bank"
