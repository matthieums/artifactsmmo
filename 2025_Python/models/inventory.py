from errors import InventoryFullError, ItemNotFoundError


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

    def contains_resources(self, items: dict):
        """Checks if all resources are found in inventory. Else returns
        a dict with the resources missing"""
        missing = dict()

        for item in items:
            code, qty = item["code"], item["quantity"]
            available = self.slots.get(code)
            if not available >= qty:
                missing[code] = qty - available
        return missing

    def get(self, item: 0):
        """Return quantity of an item in inventory. Returns 0 if item not present."""
        return self.slots.get(item, 0)

    def is_empty(self) -> bool:
        return not self.slots

    def contains(self, item) -> bool:
        return item in self.slots

    def get_inventory(self) -> dict:
        return self.slots
