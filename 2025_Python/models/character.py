from utils import get_url, post_character_action, format_loot_message
from decorators import check_character_position
import asyncio
from data import locations, SLOT_KEYS, XP_KEYS, HP_KEYS, COMBAT_KEYS
import httpx
import logging
from collections import deque
from models import Task
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
        inventory: dict,
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
            inventory={item["code"]: item["quantity"] for item in data.get("inventory", []) if item["quantity"] > 0},
            max_items=data.get("inventory_max_items"),
            combat={stat: data.get(stat) for stat in COMBAT_KEYS},
        )

    @staticmethod
    async def get_item_info(item: str) -> dict:
        url, headers = get_url(action="item_info", item=item)
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)
        return response.json()

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
        url, headers, data = get_url(character=self.name, action="move", location=location)
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
            if response.status_code == 200:
                print(f"{self.name} has moved to {location}...")
                self.update_position(location)
                data = response.json()
                await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
                return response.status_code

    def update_position(self, location):
        self.position = locations[location]

    @check_character_position
    async def fight(self, location: str) -> int:
        LOW_HP_THRESHOLD = 0.5

        if self.hp["hp"] < (LOW_HP_THRESHOLD * self.hp["max_hp"]):
            logger.info(f"{self.name} is low on HP, resting before the fight.")
            await self.rest()

        try:
            response = await post_character_action(self.name, "fight", location)
            if response is None:
                return 1

            await self.handle_fight_data(response)
            return 1

        except Exception as e:
            logger.error(f"Error in fight method: {str(e)}")
            return 1

    async def rest(self):
        response = await post_character_action(self.name, "rest")
        if response is None:
            return 1

        self.hp["hp"] = self.hp["max_hp"]

        data = response.json()
        await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
        return 1

    async def gather(self, location: str) -> int:
        # TODO: Faire une liste des errors dont j'ai besoin
        # Pour rendre le code plus parlant

        INVENTORY_FULL = 497
        action = "gather"

        try:
            response = await post_character_action(self.name, action, location)
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
        item_data = await self.get_item_info(item)
        slot = item_data["data"]["type"]

        if self.has_equipped(item):
            action = "unequip"
        else:
            action = "equip"

        url, headers, data = get_url(character=self.name, action=action, item=item, slot=slot)
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
        print(response.text)
        await self.handle_cooldown(response["data"]["cooldown"]["total_seconds"])
        return response.status_code     

    async def craft(self, item: str) -> int:
        item_data = await self.get_item_info(item)

        # Check if enough resources to build it in the inventory
        # if not, fetch everything from the bank
        # if not at the bank, TODO gather in a loop until enough resource of each

        # ingredients = item_data["data"]["craft"]["items"]

        # missing_ingredients = {}

        # for ingredient in ingredients:
        #     code, quantity = ingredient["code"], ingredient["quantity"]
        #     if (code in self.inventory and self.inventory[ingredient] >= quantity):
        #         continue
        #     missing_ingredients[ingredient["code"]] = ingredient["quantity"]

        # if missing_ingredients:
        #     for ingredient in missing_ingredients:
        #         await self.get_resource_info(ingredient)
        #         await self.gather()

        skill = item_data["data"]["craft"]["skill"]

        if not self.position == locations[skill]:
            await self.move_to(skill)

        url, headers, data = get_url(character=self.name, action="craft", item=item)
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
            if response.status_code == 471:
                return 1
            data = response.json()
            await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
            return response.status_code

    def update_inventory(self, action: str, item: str, value: int = None):
        if action in ["deposit", "empty_inventory"]:
            self.inventory[item] -= value
            if self.inventory[item] <= 0:
                del self.inventory[item]
            print(f"{value} {item} removed from {self.name}'s inventory")
            if len(self.inventory) == 0:
                print(f"{self.name}'s inventory is now empty")

        elif action in ["looted", "withdraw", "gather"]:
            self.inventory[item["code"]] = self.inventory.get(item["code"], 0) + item["quantity"]
            print(f"\t{item['quantity']} {item['code']} added to {self.name} inventory")
            return item['code'], item["quantity"]
        else:
            print("action need to be added to update inventory")

    @check_character_position
    async def empty_inventory(self, keep: list = None):
        action = "empty_inventory"

        try:
            async with httpx.AsyncClient() as client:
                for item in list(self.inventory):
                    if keep and item in keep:
                        continue
                    url, headers, data = get_url(character=self.name, item=item, quantity=self.inventory[item], action="deposit")
                    response = await client.post(url=url, headers=headers, data=data)
                    if response.status_code == 200:
                        print(f"{self.name} has deposited {self.inventory[item]} {item}")
                        self.update_inventory(action, item, self.inventory[item])
                        data = response.json()
                        await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
                return 1
        except Exception as e:
            raise Exception(f"Exception occurred during empty_inventory(): {response.text}") from e

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
                data = response.json()
                await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
                return response.status_code
            print("error during deposit")

    @check_character_position
    async def withdraw(self, item: str, quantity: int = None) -> int:
        action = "withdraw"

        if not quantity:
            quantity = self.max_items

        url, headers, data = get_url(character=self.name, item=item, quantity=quantity, action=action)
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, headers=headers, data=data)
        self.update_inventory(action, item, quantity)
        data = response.json()
        await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
        return response.status_code

    def __repr__(self):
        return self.name
