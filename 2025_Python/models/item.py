from errors import ItemNotCraftableError


class Item:
    def __init__(
            self,
            name: str,
            code: str,
            type: str,
            craftable: bool = False,
            ingredients: dict | None = None,
            skill: str | None = None
            ):
        self.name = name
        self.code = code
        self.type = type
        self.craftable = craftable
        self.ingredients = ingredients or []
        self.skill = skill or None

    @classmethod
    def from_data(cls, data):
        return cls(
            name=data.get("name"),
            code=data.get("code"),
            type=data.get("type"),
            craftable=bool(data.get("craft")),
            ingredients=data.get("craft", {}).get("items"),
            skill=data.get("craft", {}).get("skill"),
        )

    def get_ingredients(self, quantity: int | None = 1):
        if not self.craftable:
            raise ItemNotCraftableError

        return {
            ingr["code"]: ingr["quantity"] * quantity
            for ingr in self.ingredients
            }

    def __str__(self):
        return f"{self.name}"
