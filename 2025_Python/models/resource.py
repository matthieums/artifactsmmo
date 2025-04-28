from models import ItemContainer
from data import reverse_locations


class Resource(ItemContainer):
    name_of_gather = "gather"

    def __init__(self, location: str, resources: dict):
        self.location = location
        self.resources = resources

    @classmethod
    def from_data(cls, data):
        return cls(
            location=reverse_locations[(data.get("x"), data.get("y"))],
            resources={drop["code"]: "inf" for drop in data.get["drops"]}
        )

    def available(self, resources):
        return {code: self.slots.get(code, 0) for code in resources}