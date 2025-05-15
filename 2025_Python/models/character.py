from __future__ import annotations
from data import maps, XP_KEYS, HP_KEYS, COMBAT_KEYS
import logging
from typing import TYPE_CHECKING, Optional
from datetime import datetime
from dateutil import parser
import math
import asyncio
import config

from models import Item
from models.inventory import Inventory
from models.equipment import Equipment
from decorators import check_character_position
from data.utils import handle_fight_data
from errors import CharacterActionError
from utils.requests_factory import send_request
from utils.helpers import subtract_dicts, determine_action
from .character_utils import update_inventory
from .constants import IDLE
if TYPE_CHECKING:
    from models import Bank

logger = logging.getLogger(__name__)


class Character():
    def __init__(
        self,
        name: str,
        hp: dict[str[int]],
        levels: dict,
        gold: int,
        position: list,
        inventory: Inventory,
        equipment: Equipment,
        max_items: int,
        combat: dict,
        state: str = IDLE,
        bank: Optional[Bank] = None,
        ongoing_task: Optional[str] = None,
        skin: Optional[str] = None,
        cooldown_expiration: Optional[int] = None,
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
        self.cooldown_expiration = cooldown_expiration
        self.ongoing_task = ongoing_task
        self.skin = skin
        self.bank = bank
        self.state = state

    @classmethod
    async def from_api_data(
        cls,
        data: dict,
        bank: Bank,
    ) -> Character:
        inventory = Inventory.from_data(data)
        equipment = Equipment.from_data(data)
        cooldown_expiration = parser.isoparse(data.get("cooldown_expiration"))

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
            bank=bank,
            skin=data.get("skin"),
            cooldown_expiration=cooldown_expiration,
        )

        inventory.owner = character
        return character

    async def perform_task(self, task):
        await self._execute_cooldown()

        self.ongoing_task = str(task)
        logger.info(f"{self} is performing {task}")

        try:
            await task.run()
        except Exception as e:
            logger.error(f"Exception occured during task: {{str({e})}}")
            raise
        finally:
            self.ongoing_task = None

    def set_cooldown_expiration(self, expiration):
        formatted = parser.isoparse(expiration)
        self.cooldown_expiration = formatted

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
                self._update_position(location)
                return response
            elif response.status_code == 490:
                logger.info("Character is already at destination")
            else:
                logger.error(f"Error during move function: {response.text}")

    @check_character_position
    async def fight(self, location: str) -> int:

        LOW_HP_THRESHOLD = 0.5
        action = "fight"

        if self.hp["hp"] < (LOW_HP_THRESHOLD * self.hp["max_hp"]):
            logger.info(f"{self.name} is low on HP, resting before the fight.")
            await self.rest()

        try:
            response = await send_request(
                self,
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
                self._update_position("spawn")
                self.move_to(location)

            await handle_fight_data(self, response)

    async def rest(self):

        try:
            await send_request(self, action="rest")
        except Exception as e:
            logger.error(f"Error in fight method: {str(e)}")
            return 1
        else:
            self.hp["hp"] = ["max_hp"]
            return 1

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
                    self,
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
                    update_inventory(self, item=code, quantity=qty)

                    if code == resource:
                        remaining -= qty

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
                        character=self,
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
                        update_inventory(self, code, -qty)
                    for result_data in data["details"]["items"]:
                        update_inventory(
                            self,
                            result_data.get("code"),
                            result_data.get("quantity")
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

    @check_character_position
    async def deposit_all(self, exceptions: list = None) -> int:
        for item in list(self.inventory):
            code, qty = item
            if item not in exceptions:
                try:
                    await self.deposit(qty, code)
                except Exception as e:
                    logger.error(f"Error during empty inventory: {str(e)}")
                    raise

    @check_character_position
    async def deposit(self, quantity: int = None, item: str = None) -> int:

        try:
            await self.bank.deposit(self, quantity, item)
        except Exception as e:
            logger.error(f"Error during deposit: {str(e)}")
            raise

    @check_character_position
    async def withdraw(self, item: str, quantity: int = None) -> int:
        await self.bank.withdraw(self, item, quantity)

    def __repr__(self):
        return self.name

    def _update_position(self, location):
        self.position = maps[location]

    async def _execute_cooldown(self) -> None:
        now = datetime.now(config.local_tz)
        expiration = self.cooldown_expiration

        seconds = max(0.0, math.ceil((expiration - now).total_seconds()))

        if seconds > 0.01:
            logger.info(f"{self} is on cooldown for {seconds} seconds...")

        await asyncio.sleep(seconds)
        return
