class Equipment():
    SLOTS = [
        "weapon",
        "rune",
        "shield",
        "helmet",
        "body_armor",
        "leg_armor",
        "boots",
        "ring1",
        "ring2",
        "amulet",
        "artifact1",
        "artifact2",
        "artifact3",
        "utility1",
        "utility1_quantity",
        "utility2",
        "utility2_quantity",
        "bag",
    ]

    def __init__(self, **kwargs):
        for slot in self.SLOTS:
            setattr(self, slot, kwargs.get(slot, None))

    @classmethod
    def from_data(cls, data):
        slots = {slot: data.get(f"{slot}_slot") for slot in cls.SLOTS if not slot.endswith("_quantity")}
        slots["utility1_quantity"] = data.get("utility1_slot_quantity")
        slots["utility2_quantity"] = data.get("utility2_slot_quantity")
        return cls(**slots)

    def __repr__(self):
        equipped = {slot: getattr(self, slot) for slot in self.SLOTS if getattr(self, slot)}
        return f"{equipped}"


    # def equip(self, item):
    #     # Get item type
    #     # If item type not of type armor, False
    #     # If slot is already occupied, unequip
    #     # equip new item
    #     # Update inventory
    #     return NotImplementedError
