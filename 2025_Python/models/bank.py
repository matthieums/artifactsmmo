# How to update the bank during the script? I mean you could just destroy the bank
# and recreate it based on the fetched data.

import httpx
from utils import send_request
import logging

logger = logging.getLogger(__name__)


class Bank:
    def __init__(self, slots: dict, gold: int, inventory):
        self.slots = slots
        self.gold = gold
        self.inventory = inventory

    @classmethod
    def from_api_data(cls, details, items) -> "Bank":
        try:
            slots = details.get("slots", 0),
            gold = details.get("gold", 0),

            inventory = {
                item["code"]: item["quantity"] for item in items
            }
            return cls(slots=slots, gold=gold, inventory=inventory)
        except Exception as e:
            logger.error(f"Error initializing Bank from API data: {e}")
            raise

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

    def get(self, item: str) -> int:
        return self.slot.get(item, 0)

    def contains_resources(self, items: dict) -> tuple:
        """Checks if all resources are found in inventory. Else returns
        two dicts. One with the resources missing, one with the resources found"""
        missing = dict()
        found = dict()

        for item in items:
            code, qty = item["code"], item["quantity"]
            available = self.get(code)
            if available:
                found[code] = available
            if not available >= qty:
                missing[code] = qty - available
        missing.update({"location": "bank"})

        return found, missing
