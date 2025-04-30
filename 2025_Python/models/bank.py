# How to update the bank during the script? I mean you could just destroy the bank
# and recreate it based on the fetched data.

from utils import send_request
import logging
from models import ItemContainer, Item

logger = logging.getLogger(__name__)


class Bank(ItemContainer):
    name_of_gather = "withdraw"

    def __init__(self, slots: dict, gold: int, inventory):
        self.slots = slots
        self.gold = gold
        self.inventory = inventory
        self.reserved = defaultdict(dict)
        self.lock = asyncio.Lock()

    @classmethod
    def from_api_data(cls, details, items) -> "Bank":
        slots = details.get("slots")
        gold = details.get("gold")

        if not slots or not gold:
            raise ValueError("Missing required fields: 'slots' or 'gold'.")

        inventory = {
            item["code"]: item["quantity"] for item in items
        }
        return cls(slots=slots, gold=gold, inventory=inventory)

    @classmethod
    async def get_bank_details(cls):

        response = response = await send_request(action="bank_details")
        data = response.json()["data"]
        if response.is_success:
            data = response.json()["data"]
            return data
        else:
            raise Exception("Problem during bank initialization")

    @classmethod
    async def get_bank_items(cls):
        response = await send_request(action="bank_items")
        if response.is_success:
            data = response.json()["data"]
            return data
        else:
            raise Exception("Problem during bank initialization")

    def get(self, item: str | Item) -> dict:
        code = item if not item.isinstance(Item) else item.code

        quantity = self.inventory.get(code, 0)

        return quantity

    def available(self, items: dict) -> dict:
        """Returns a dictionary of the available items found
        in the bank {code: qty}"""
        return {code: self.inventory.get(code, 0) for code in items}

    def __str__(self):
        return "bank"
