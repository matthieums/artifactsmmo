
class Inventory:
    def __init__(self, character: object, slots: dict, max_capacity: int):
        self.owner = character
        self.slots = slots
        self.max_capacity = 0

    @classmethod
    def from_data(cls, data, character):
        return cls(
            slots={
                item["code"]: item["quantity"]
                for item in data.get("inventory", [])
                if item["quantity"] > 0
                },
            max_capacity=data.get("inventory_max_items"),
            character=character
        )

    def add(self, item, quantity):
        owned = self.slots.get(item, 0)
        if (
            item in self.slots and
            owned + quantity > self.max_capacity
        ):
            self.slots[item] = owned + quantity
        else:
            print(f"Not enough space to add {item} to {self.owner}'s inventory")

    def remove(self, item, quantity):
        if item not in self.slots:
            print("No such item in inventory")

        self.slots[item] = self.slots.get(item) - quantity

        if self.slots[item] < 0:
            del self.slots[item]
        # update

    def occupied_space(self):
        return sum(self.slots.values())

    def free_space(self):
        return (self.occupied_space() - self.max_capacity)

    def contains_resources(self, item, quantity):
        return self.slots.get(item) >= quantity
