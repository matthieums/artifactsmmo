from utils import send_request, format_loot_message, get_item_info, get_map_data, find_resources
from decorators import check_character_position
import asyncio
from data import locations, SLOT_KEYS, XP_KEYS, HP_KEYS, COMBAT_KEYS
import logging
from collections import deque
from models import Task, Inventory, Item, Bank
from errors import CharacterActionError
from utils import subtract_dicts


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
        self.cooldown_duration = 0
        self.cooldown_expiration = None
        self.bank = None

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

    async def handle_response_cooldown(self, data: dict) -> None:
        value = data["data"]["cooldown"]["total_seconds"]
        cooldown = value
        print(f"{self.name} is on cooldown for {cooldown} seconds...")
        await asyncio.sleep(cooldown)
        self.cooldown_duration = 0
        return

    def enqueue_task(self, task):
        self.task_queue.append(task)

    def add_task(self, iterations: int, method: Callable[..., Any], *args, **kwargs):

        if not callable(method):
            raise AttributeError(f"'{method} is not a valid method")

        for _ in range(iterations):
            task = Task(method=method, args=args, kwargs=kwargs)
            self.enqueue_task(task)

    async def run_tasks(self):
        while self.task_queue:
            task = self.task_queue.popleft()
            await task.run()

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
            await self.handle_response_cooldown(data)

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

        await self.handle_response_cooldown(data)

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
                await self.handle_response_cooldown(data)
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
            await self.handle_response_cooldown(data)
            return 1

    def is_at_location(self, location: str):
        return self.position == locations[location]

    @check_character_position
    async def gather(self, quantity: int, resource: str, location: str = None) -> int:
        action = determine_action(location)
        remaining = quantity

        if self.inventory.is_full():
            await self.empty_inventory()

        while remaining > 0:
            try:
                response = await send_request(self.name, action=action, location=location)
            except Exception as e:
                logging.error(f"Action '{action}' failed for {self.name} at {location}. \n{e}")
                return 0
            else:
                if not response.is_success:
                    raise CharacterActionError(response, self.name, action, location)

                data = response.json()
                looted_items = data["data"]["details"]["items"]

                for loot in looted_items:
                    code, qty = loot.get("code"), loot.get("quantity")
                    self.update_inventory(item=code, quantity=qty)

                    if code == resource:
                        remaining -= qty

                await self.handle_cooldown(data["data"]["cooldown"]["total_seconds"])

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
            await self.handle_response_cooldown(response["data"]["cooldown"]["total_seconds"])
            return response.status_code

    @check_character_position
    async def craft(self, item: str, quantity: int | None = 1) -> int:
        """Attempts to craft an item from inventory resources.
        If resources are missing, queues tasks to find them, re-enqueues
        itself, and returns."""
        action = "craft"

        item_data = await get_item_info(item)
        item_object = Item.from_data(item_data["data"])
        ingredients_needed = item_object.get_ingredients(quantity)

        # Craft immediately if all items are inventory
        if self.inventory.contains(ingredients_needed):
            for _ in range(quantity):
                try:
                    response = await send_request(character=self.name, action=action, item=item)
                except Exception as e:
                    logging.error(f"{self.name} failed to craft {item}. \n{e}")
                else:
                    data = response.json()
                    for ingredient in ingredients_needed:
                        code, qty = ingredient["code"], ingredient["quantity"]
                        self.inventory.remove(item=code, quantity=qty)
                    self.inventory.add(item=item, quantity=1)
                    await self.handle_response_cooldown(data)
            return 1

        # sources = [self.inventory: Inventory, self.bank: Bank]
        # #  If missing ingredients, check what's in the inventory
        # async def gather_ingredients(items: dict, sources: list):
        #     for source in sources:

        available_in_inventory = self.inventory.available(ingredients_needed)
        if available_in_inventory:
            ingredients_needed = subtract_dicts(ingredients_needed, available_in_inventory)

        if ingredients_needed:
            available_in_bank = self.bank.available(ingredients_needed)
            if available_in_bank:
                ingredients_needed = subtract_dicts(ingredients_needed, available_in_bank)

                bank_kwargs = []
                for code, qty in available_in_bank.items():
                    bank_kwargs.append({
                        "location": "bank",
                        "item": code,
                        "quantity": qty
                    })

                for kwargs in bank_kwargs:
                    await self.prepare_task_data(**kwargs)

            if ingredients_needed:
                resources_locations = find_resources(ingredients_needed)

                world_kwargs = []
                for location, code in resources_locations.items():
                    world_kwargs.append({
                        "location": location,
                        "item": code,
                        "quantity": ingredients_needed[code]
                    })

                for kwargs in world_kwargs:
                    await self.prepare_task_data(**kwargs)

    async def prepare_task_data(self, location: str, item: str, quantity: int):
        # Now build kwargs {location: location, code: code, qty: qty}
        # {location: "bank", code: "copper_rocks", qty: 4}
        # {location: "copper_rocks", code: "copper_ore", qty: 50}
        # {location: "iron_rocks", code: "iron_ore", qty: 25}

        if not location:
            logger.error("No location provided to the fetch data function")

        # TODO: This will be a problem if I call craft on multiple characters at the
        # same time.
        if location == "bank":
            method_name = "withdraw"
            self.add_task(iterations=1, method_name=method_name, item=item, quantity=quantity)

        elif location == "world":
            try:
                map_data = await get_map_data(location)
                data = map_data.json()["data"]
            except Exception as e:
                logger.error(f"Cannot fetch data for location {location}. {str(e)}")
                return 0
            else:
                map_type = data["content"]["type"]
                if map_type == "monster":
                    method_name = "fight"
                elif map_type == "resource":
                    method_name = "gather"
                else:
                    logger.error(f"Unknown map type: {map_type}")

            self.add_task(iterations=1, method_name=method_name, location=location)

        # TODO: Now, I need to adapt my task runner to run until a condition is fulfilled.
        # In this case, until the quantity is gathered or looted
        return

    def update_inventory(self, action: str, item: str, quantity: int | None = None):
        try:
            if action in ["deposit", "empty_inventory"]:
                self.inventory.remove(item, quantity)
                return

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
            await self.handle_response_cooldown(data)
            return response.status_code

    def __repr__(self):
        return self.name
