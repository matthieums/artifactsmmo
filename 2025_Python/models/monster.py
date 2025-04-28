from models import ItemContainer
from data import reverse_locations


class Monster(ItemContainer):
    name_of_gather = "fight"

    def __init__(self, location: str, resources: list, code: str):
        self.code = code
        self.location = location
        self.resources = resources

    @classmethod
    def from_data(cls, map_data, monster_data):
        return cls(
            code=monster_data.get("code"),
            location=reverse_locations[(map_data.get("x"), map_data.get("y"))],
            resources={drop["code"]: "inf" for drop in monster_data.get["drops"]}
        )

    def available(self, resources):
        return {code: self.slots.get(code, 0) for code in resources}