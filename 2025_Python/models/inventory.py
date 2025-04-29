from errors import InventoryFullError, ItemNotFoundError
from models import Item


class Inventory:
    def __init__(self, owner: object, slots: dict, max_capacity: int):
        self.owner = owner
        self.slots = slots
        self.max_capacity = max_capacity

    @classmethod
    def from_data(cls, data: dict, owner: object):
        return cls(
            slots={
                item["code"]: item["quantity"]
                for item in data.get("inventory", [])
                if item["quantity"] > 0
                },
            max_capacity=data.get("inventory_max_items"),
            owner=owner
        )

    def add(self, item: str, quantity: int | None) -> None:
        if quantity and quantity <= self.free_space():
            self.slots[item] = self.get(item) + quantity
        else:
            raise InventoryFullError(f"Not enough space to add {item} to {self.owner}'s inventory")

    def remove(self, item, quantity: int | None = None):
        if item not in self.slots:
            print(f"No {item} found in {self.owner}'s inventory. Cannot remove.")
            raise ItemNotFoundError

        elif not quantity:
            del self.slots[item]
            print(f"All {item} removed from {self.owner}'s inventory.")
            return 1

        else:
            self.slots[item] = self.slots[item] - quantity
            print(f"{quantity} {item} removed from {self.owner}'s inventory")
            if self.slots[item] < 0:
                del self.slots[item]
                print(f"No more {item} in {self.owner}'s inventory")
            return 1

    def occupied_space(self):
        return sum(self.slots.values())

    def free_space(self):
        return (self.max_capacity - self.occupied_space())

    def available(self, items: dict) -> dict:
        """Returns a dict of items found
        in the inventory {code: qty}"""
        return {code: self.slots.get(code, 0) for code in items}

    def get(self, item: str | Item):
        """Return quantity of an item in inventory. Returns 0 if item not present."""
        code = item if isinstance(item, str) else item.code

        quantity = self.slots.get(code, 0)

        return quantity

    def is_empty(self) -> bool:
        return not self.slots

    def is_full(self) -> bool:
        return self.occupied_space() == self.max_capacity

    def contains_everything(self, items: dict) -> bool:
        return all(self.slots.get(code, 0) >= qty for code, qty in items.items())

    def get_inventory(self) -> dict:
        return self.slots
