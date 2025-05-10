from errors import InventoryFullError, ItemNotFoundError
from models import Item, Bank
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class Inventory:
    def __init__(self, owner: object, slots: defaultdict, max_capacity: int):
        self.owner = owner
        self.slots = slots
        self.max_capacity = max_capacity

    @classmethod
    def from_data(cls, data: list) -> "Inventory":
        return cls(
            slots=defaultdict(int, {
                slot["code"]: slot["quantity"]
                for slot in data.get("inventory", [])
                if slot["quantity"] > 0 and slot["code"] != ""
            }),
            max_capacity=data.get("inventory_max_items"),
            owner=None
        )

    def add(self, item: str, quantity: int) -> None:
        if quantity <= self.free_space():
            self.slots[item] += quantity
        else:
            raise InventoryFullError(
                f"Not enough space to add {item} to"
                f"{self.owner}'s inventory"
                )

    def remove(self, item, quantity: int):
        if item not in self.slots:
            print(
                f"No {item} found in {self.owner}'s inventory. Cannot remove."
            )
            raise ItemNotFoundError

        self.slots[item] -= quantity
        print(f"{quantity} {item} removed from {self.owner}'s inventory")

        if self.slots[item] < 0:
            del self.slots[item]
            print(f"No more {item} in {self.owner}'s inventory")
        return 1

    async def empty(self, bank: "Bank", keep: list | None):
        """Empty the inventory in the bank."""
        keep = keep or []

        if self.is_empty():
            logger.error("Nothing to deposit")
            return

        for item, quantity in dict(self).items():
            try:
                await bank.deposit(self.owner, item, quantity)
            except Exception as e:
                logger.error(f"Error in empty method: {str(e)}")

    def occupied_space(self):
        return sum(self.slots.values())

    def free_space(self):
        return (self.max_capacity - self.occupied_space())

    def available(self, items: dict) -> dict:
        """Returns a dict of items found
        in the inventory {code: qty}"""
        return {code: self.slots.get(code) for code in items}

    def get(self, item: str | Item):
        """Return quantity of an item in inventory. Returns 0 if item not
        present."""
        code = item if isinstance(item, str) else item.code

        quantity = self.slots.get(code, 0)

        return quantity

    def is_empty(self) -> bool:
        return not self.slots

    def is_full(self) -> bool:
        return self.occupied_space() == self.max_capacity

    def contains_everything(self, items: dict) -> bool:
        logger.debug("items needed: ", items)
        return all(
            self.slots.get(code, 0) >= qty for code, qty in items.items()
            )

    async def has_enough_space(self, space: int):
        if not self.free_space() >= space:
            return False

    def __iter__(self):
        return iter(self.slots.items())

    def __len__(self):
        return len(self.slots)

    def __contains__(self, item):
        return item in self.slots

    def __str__(self):
        return f"{self.slots}"