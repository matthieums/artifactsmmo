from utils import send_request, make_post_request, format_loot_message, get_item_info
from decorators import check_character_position
import asyncio
from data import locations, SLOT_KEYS, XP_KEYS, HP_KEYS, COMBAT_KEYS
import httpx
import logging
from collections import deque
from models import Task, Inventory, Item
from errors import CharacterActionError

logger = logging.getLogger(__name__)


class Character():
    def __init__(
        self,
        name: str,
        hp: dict,
        levels: dict,
        gold: int,
        position: list,
        equipment: dict,
        inventory: Inventory,
        max_items: int,
        combat: dict,
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
        self.task_queue = deque()
        self.cooldown_expiration = None
        self.cooldown_duration = 0

    @classmethod
    def from_api_data(cls, data: dict) -> "Character":
        return cls(
            name=data.get("name"),
            gold=data.get("gold"),
            levels={key: data.get(key) for key in XP_KEYS},
            position=[data.get("x"), data.get("y")],
            hp={stat: data.get(stat) for stat in HP_KEYS},
            equipment={slot: data.get(slot, "") for slot in SLOT_KEYS},
            inventory=None,
            max_items=data.get("inventory_max_items"),
            combat={stat: data.get(stat) for stat in COMBAT_KEYS},
        )

    def is_on_cooldown(self):
        return self.cooldown_duration > 0

    async def handle_cooldown(self, value: int) -> None:
        cooldown = value
        print(f"{self.name} is on cooldown for {cooldown} seconds...")
        await asyncio.sleep(cooldown)
        self.cooldown_duration = 0
        return

    def enqueue_task(self, task):
        self.task_queue.append(task)

    def build_task(self, iterations: int | None, method_name: str, *args, **kwargs):
        method = getattr(self, method_name, None)

        if not callable(method):
            raise AttributeError(f"'{method_name} is not a valid method")

        task = Task(method, iterations, *args, **kwargs)
        self.enqueue_task(task)

    async def run_tasks(self):
        while self.task_queue:
            task = self.task_queue.popleft()
            result = await task.run()
            if result == 1:
                continue

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

    async def handle_fight_data(self, response):
        logger.info("handling fight data")

        data = response.json()
        loot = {}
        items = {}
        fight_data = data['data']['fight']
        fight_result = fight_data['result']

        if fight_result == "loss":
            self.update_position("spawn")
            print(f"{self.name} has died")
            await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])

        print(f"{self.name} has won the fight")
        loot["gold"] = self.update_gold(fight_data["gold"])
        logger.info("GOLD updated")

        if fight_data["drops"]:
            for item in fight_data["drops"]:
                item_name, quantity = self.update_inventory(action="looted", item=item)
                items[item_name] = quantity
            loot["items"] = items
            logger.info("INVENTORY updated")

        loot["xp"] = fight_data.get("xp")

        self.update_hp(data["data"]["character"]["hp"])
        logger.info("HP updated")

        format_loot_message(self.name, loot)

        await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])

        return 1

    async def move_to(self, location: str) -> int:
        try:
            response = await send_request(self.name, action="move", location=location)
        except Exception as e:
            logger.error(f"Error in move method: {str(e)}")
            return 1
        else:
            if response.status_code == 200:
                print(f"{self.name} has moved to {location}...")
                self.update_position(location)
                data = response.json()
                await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
                return response
            logger.error("Error during move function")

    def update_position(self, location):
        self.position = locations[location]

    @check_character_position
    async def fight(self, location: str) -> int:
        LOW_HP_THRESHOLD = 0.5

        if self.hp["hp"] < (LOW_HP_THRESHOLD * self.hp["max_hp"]):
            logger.info(f"{self.name} is low on HP, resting before the fight.")
            await self.rest()

        try:
            response = await send_request(self.name, action="fight", location=location)
            if response is None:
                return 1

            await self.handle_fight_data(response)
            return 1

        except Exception as e:
            logger.error(f"Error in fight method: {str(e)}")
            return 1

    async def rest(self):
        try:
            response = await send_request(self.name, action="rest")
        except Exception as e:
            logger.error(f"Error in fight method: {str(e)}")
            return 1
        else:
            if response is None:
                return 1

            self.hp["hp"] = self.hp["max_hp"]

            data = response.json()
            await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
            return 1

    @check_character_position
    async def gather(self, location: str) -> int:

        INVENTORY_FULL = 497
        action = "gather"

        try:
            response = await send_request(self.name, action=action, location=location)
        except Exception as e:
            logging.error(f"Action '{action}' failed for {self.name} at {location}. \n{e}")
            return 0

        # Write success message in the task class?
        if response.is_success:
            data = response.json()

            for item in data["data"]["details"]["items"]:
                self.update_inventory(action=action, item=item)
            await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
            return

        elif not response.is_success:
            if response.status_code == INVENTORY_FULL:
                return 1
            else:
                raise CharacterActionError(response, self.name, action, location)

    def has_equipped(self, item: str):
        return item in self.equipment.values()

    async def toggle_equipped(self, item: str) -> int:
        # TODO: Check if already unequipped
        item_data = await get_item_info(item)
        slot = item_data["data"]["type"]

        if self.has_equipped(item):
            action = "unequip"
        else:
            action = "equip"

        try:       
            response = await send_request(character=self.name, action=action, item=item, slot=slot)
        except Exception as e:
            logger.error(f"Error in fight method: {str(e)}")
            return 1
        else:
            await self.handle_cooldown(response["data"]["cooldown"]["total_seconds"])
            return response.status_code

    @check_character_position
    async def craft(self, item: str, quantity: int | None = 1) -> int:
        action = "craft"
        
        item_data = await get_item_info(item)
        item_object = Item.from_data(item_data["data"])

        # 1. Check if enough resources in inventory to craft item
        if not await self.can_craft(item_object, quantity):
            # TODO: Find out missing resources
            # Check if they are available in bank, else trigger gather
                # I will need a table "lootable_from" for the character to know
                # where he should be getting the resource.
                # That's where the queuing starts. I will need to find out
                # all the steps needed and either create a subqueue or enqueue
                # the tasks in reverse order
            # If items in the resources that I don't have, craft them
            # Fetch resources
            # Try crafting again
            return

        ingredients = item_object.get_ingredients()

        # 2. Craft items
        for _ in range(quantity):
            try:
                response = await send_request(character=self.name, action=action, item=item)
            except Exception as e:
                logging.error(f"{self.name} failed to craft {item}. \n{e}")
            else:
                data = response.json()
                for ingredient in ingredients:
                    code, qty = ingredient["code"], ingredient["quantity"]
                    self.inventory.remove(item=code, quantity=qty)
                self.inventory.add(item=item, quantity=1)
                await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
        return 1

    async def can_craft(self, item: Item, amount: int) -> bool:
        """Checks if character has enough resources to craft the desired
        amount of items"""

        recipe = item.get_ingredients(amount)

        for ingredient in recipe:
            code, qty = ingredient["code"], ingredient["quantity"]
            if not self.inventory.contains_resources(code, qty):
                missing_value = qty - self.inventory.get(code)
                print(f"missing {missing_value} {code} to craft {amount} {item}")
                return False
        return True

    def update_inventory(self, action: str, item: str, value: int | None = None):
        try:
            if action in ["deposit", "empty_inventory"]:
                self.inventory.remove(item, value)
                return

            elif action in ["looted", "withdraw", "gather"]:
                self.inventory.add(item, value)
                return

            else:
                raise ValueError(f"Unsupported inventory action: {action}")
        except Exception as e:
            logging.error(f"An error occured: {e}")
            return None

    @check_character_position
    async def empty_inventory(self, keep: list = None):
        action = "empty_inventory"

        if self.inventory.is_empty():
            print("Nothing to deposit.")

        for item, quantity in dict(self.inventory.get_inventory()).items():
            if keep and item in keep:
                continue
            try:
                response = await send_request(character=self.name, item=item, quantity=quantity, action="deposit")
            except Exception as e:
                logger.error(f"Error in empty_inventory method: {str(e)}")
                return 1
            else:
                if response.status_code == 200:
                    quantity = self.inventory.get(item)
                    print(f"{self.name} has deposited {quantity} {item}")
                    self.update_inventory(action, item)
                    data = response.json()
                    await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])

    @check_character_position
    async def deposit(self, quantity: int = None, item: str = None) -> int:
        action = "deposit"

        if not self.inventory.contains(item):
            print(f"There is no {item} to deposit")
            return 0

        available = self.inventory.get(item)

        if quantity and quantity <= available:
            deposit_amount = quantity
        else:
            deposit_amount = available

        try:
            response = await send_request(character=self.name, item=item, quantity=deposit_amount, action=action)
        except Exception as e:
            logger.error(f"Error in empty_inventory method: {str(e)}")
            return 0
        else:
            if response.status_code == 200:
                self.update_inventory(action, item, deposit_amount)
                data = response.json()
                await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
                return 1
            print("error during deposit")

    @check_character_position
    async def withdraw(self, item: str, quantity: int = None) -> int:
        action = "withdraw"

        free_space = self.inventory.free_space()

        # TODO: Check if bank has enough of required items BEFORE moving

        # Check if character has enough space for the required item quantity
        if quantity and quantity <= free_space:
            withdraw_amount = quantity
        else:
            withdraw_amount = free_space
            print(f"{self.name} can only withdraw {free_space} at the moment")
        try:
            response = await send_request(character=self.name, item=item, quantity=withdraw_amount, action=action)
        except Exception as e:
            logging.error(f"{self.name} failed to '{action}'. \n{e}")
            return 0
        else:
            self.update_inventory(action, item, quantity)
            data = response.json()
            print(f"{self.name} withdrew {withdraw_amount} {item}")
            await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
            return response.status_code

    def __repr__(self):
        return self.name
