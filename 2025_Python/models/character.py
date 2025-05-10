from __future__ import annotations
import asyncio
from data import maps, XP_KEYS, HP_KEYS, COMBAT_KEYS
import logging
from typing import TYPE_CHECKING, Optional

from models import Item
from models.inventory import Inventory
from models.equipment import Equipment
from decorators import check_character_position
from data.utils import handle_fight_data
from errors import CharacterActionError
from utils.requests_factory import send_request
from utils.helpers import subtract_dicts, determine_action


if TYPE_CHECKING:
    from models import Bank

logger = logging.getLogger(__name__)


class Character():
    def __init__(
        self,
        name: str,
        hp: dict,
        levels: dict,
        gold: int,
        position: list,
        inventory: Inventory,
        equipment: Equipment,
        max_items: int,
        combat: dict,
        bank: Optional[Bank] = None,
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
        self.cooldown_duration = 0
        self.cooldown_expiration = None
        self.bank = bank

    @classmethod
    def from_api_data(cls, data: dict, bank: Bank) -> Character:
        inventory = Inventory.from_data(data)
        equipment = Equipment.from_data(data)

        character = cls(
            name=data.get("name"),
            gold=data.get("gold"),
            levels={key: data.get(key) for key in XP_KEYS},
            position=[data.get("x"), data.get("y")],
            hp={stat: data.get(stat) for stat in HP_KEYS},
            equipment=equipment,
            inventory=inventory,
            max_items=data.get("inventory_max_items"),
            combat={stat: data.get(stat) for stat in COMBAT_KEYS},
            bank=bank
        )

        inventory.owner = character
        return character

    def is_on_cooldown(self):
        return self.cooldown_duration > 0

    async def handle_cooldown(self, seconds: int | None = None) -> None:
        if seconds is None:
            seconds = self.cooldown_duration

        if seconds > 0:
            logger.info(f"{self.name} is on cooldown for {seconds} seconds...")

        await asyncio.sleep(seconds)
        self.cooldown_duration = 0
        return

    def update_gold(self, quantity: int) -> int:
        """Add a negative or positive value to the character's gold count"""
        if quantity > 0:
            print(f"{self.name} received {quantity} gold")
        elif quantity < 0:
            print(f"{self.name} lost {quantity} gold")
        self.gold += quantity
        return quantity

    def update_hp(self, value: int) -> int:
        """Add a negative or positive value to the character's hp count"""
        if self.hp["hp"] > value:
            print(f"{self.name} gained {abs(self.hp['hp'] - value)} hp")
        elif self.hp["hp"] < value:
            print(f"{self.name} lost {abs(self.hp['hp'] - value)} hp")
        else:
            print("no hp gain nor loss")
        self.hp["hp"] = value
        return 1

    async def move_to(self, location: str) -> int:
        if location not in maps:
            logger.error("Undefined location")
            raise ValueError("Map doesn't exist in data.")

        try:
            response = await send_request(
                self,
                action="move",
                location=location
            )
        except Exception as e:
            logger.error(f"Error in move method: {str(e)}")
            return 1
        else:
            if response.status_code == 200:
                print(f"{self.name} has moved to {location}...")
                self.update_position(location)
                data = response.json()
                await self.handle_cooldown(
                    data["data"]["cooldown"]["total_seconds"]
                )
                return response
            elif response.status_code == 490:
                logger.info("Character is already at destination")
            else:
                logger.error(f"Error during move function: {response.text}")


    def update_position(self, location):
        self.position = maps[location]

    @check_character_position
    async def fight(self, location: str) -> int:
        LOW_HP_THRESHOLD = 0.5
        action = "fight"

        if self.hp["hp"] < (LOW_HP_THRESHOLD * self.hp["max_hp"]):
            logger.info(f"{self.name} is low on HP, resting before the fight.")
            await self.rest()

        try:
            response = await send_request(
                self.name,
                action=action,
                location=location
            )
        except Exception as e:
            logger.error(f"Error in fight method: {str(e)}")
            return
        else:
            data = response.json()
            result = data['data']['fight']['result']
            if result == "loss":
                logger.info(f"{self} died during a fight")
                self.update_position("spawn")
                self.move_to(location)

            await handle_fight_data(self, response)
            await self.handle_cooldown(
                data["data"]["cooldown"]["total_seconds"]
                )

    async def rest(self):
        try:
            response = await send_request(self.name, action="rest")
        except Exception as e:
            logger.error(f"Error in fight method: {str(e)}")
            return 1
        else:
            self.update_hp(self.hp["max_hp"])

            data = response.json()
            await self.handle_cooldown(
                data["data"]["cooldown"]["total_seconds"]
                )
            return 1

    def is_at_location(self, location: str):
        return self.position == maps[location]

    @check_character_position
    async def gather(
        self,
        resource: str,
        quantity: int = None,
        location: str = None
    ) -> int:
        action = determine_action(location)
        remaining = quantity or float("inf")

        while remaining > 0:
            if self.inventory.is_full():
                await self.empty_inventory()
            try:
                response = await send_request(
                    self.name,
                    action=action,
                    location=location
                    )
            except Exception as e:
                logging.error(f"Action '{action}' failed for {self.name} at"
                              f"{location}. \n{e}")
                return 0
            else:
                if not response.is_success:
                    raise CharacterActionError(
                        response,
                        self.name,
                        action,
                        location
                    )
                data = response.json()
                looted_items = data["data"]["details"]["items"]

                for loot in looted_items:
                    code, qty = loot.get("code"), loot.get("quantity")
                    self.update_inventory(item=code, quantity=qty)

                    if code == resource:
                        remaining -= qty

                await self.handle_cooldown(
                    data["data"]["cooldown"]["total_seconds"]
                    )

    def has_equipped(self, item: str):
        return item in self.equipment.values()

    async def equip(self, item_code: str) -> int:
        item = await Item.load(item_code)
        await self.equipment.equip(self, item)

    async def unequip(self, item_code):
        item = await Item.load(item_code)
        await self.equipment.unequip(self, item)

    async def craft(self, item_code: str, quantity: int | None = 1) -> int:
        """Attempts to craft an item from inventory resources.
        If resources are missing, finds them before crafting."""
        action = "craft"
        inventory = self.inventory
        kwargs = {"item_code": item_code, "quantity": quantity}
        item_object = await Item.load(item_code)
        needed = item_object.get_ingredients(quantity)
        bank = self.bank

        ingredients_needed = item_object.get_ingredients(quantity)

        # Craft immediately if all items are inventory

        if self.inventory.contains_everything(needed):
            logger.debug(f"{self}'s inventory contains everything for crafting"
                         f"{item_code}")
            if self.position != maps[item_object.skill]:
                await self.move_to(item_object.skill)

            for _ in range(quantity):
                try:
                    response = await send_request(
                        character=self.name,
                        action=action,
                        item=item_code
                        )
                except Exception as e:
                    logger.error(f"{self.name} failed to craft {item_code}."
                                 f"\n{e}")
                    logger.error("response: ", response.text)
                else:
                    data = response.json()["data"]
                    # TODO: Refactor update_inventory because of "-"
                    for code, qty in ingredients_needed.items():
                        self.update_inventory(code, -qty)
                    for result_data in data["details"]["items"]:
                        self.update_inventory(
                            result_data.get("code"),
                            result_data.get("quantity")
                            )
                    await self.handle_cooldown(
                        data["cooldown"]["total_seconds"]
                        )
            return 1

        logger.debug(f"{self}'s inventory misses ingredients for crafting"
                     f"{item_code}")

        space_needed = sum(needed.values())

        if not await inventory.has_enough_space(space_needed):
            if inventory.max_capacity >= space_needed:
                await self.empty_inventory()
                return await self.craft(**kwargs)
            else:
                logger.error("Not enough space in inventory to craft")
                return ValueError(
                    f"Too many items for {self}'s inventory capacity"
                    )

        available_in_inventory = self.inventory.available(needed)

        logger.debug(
            f"{self} already has {available_in_inventory} in his inventory")

        self.update_based_on_available_resources(
            available_in_inventory,
            needed
            )

        logger.debug(f"{self} needs {needed}")

        async with bank.lock:
            available_in_bank = bank.available(needed)
            await bank.reserve(self, available_in_bank)

        self.update_based_on_available_resources(available_in_bank, needed)

        # Withdraw from the bank
        withdrawn = {}
        for code, quantity in available_in_bank.items():
            try:
                await self.withdraw(code, quantity)
            except Exception:
                logger.error(
                    f"""
                    Error during gathering of crafting ingredients.
                    {self} will now return everything to the bank
                    """
                )
                return await self.empty_inventory()
            else:
                withdrawn[code] = quantity
                async with bank.lock:
                    await bank.clear_reservation(self, code)

        self.update_based_on_available_resources(withdrawn, needed)

        # Gather from the world
        for code, quantity in needed.items():
            await self.gather(quantity=quantity, resource=code)
        return await self.craft(**kwargs)

    def update_based_on_available_resources(
            self,
            available: dict,
            materials: dict
            ) -> dict:
        missing_from_source = subtract_dicts(materials, available)
        return missing_from_source

    def update_inventory(self, item: str, quantity: int):
        if quantity > 0:
            self.inventory.add(item, quantity)
        elif quantity < 0:
            self.inventory.remove(item, abs(quantity))
        else:
            logger.error("Invalid quantity provided to update_inventory")

    @check_character_position
    async def empty_inventory(self, keep: list = None) -> int:
        """Delegation pattern. Calls the empty method on the
        character's inventory."""
        await self.inventory.empty(self.bank, keep)
        return 1

    @check_character_position
    async def deposit(self, quantity: int = None, item: str = None) -> int:
        await self.bank.deposit(self, quantity, item)

    @check_character_position
    async def withdraw(self, item: str, quantity: int = None) -> int:
        await self.bank.withdraw(self, item, quantity)

    def __repr__(self):
        return self.name
