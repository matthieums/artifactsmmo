# How to update the bank during the script? I mean you could just destroy the bank
# and recreate it based on the fetched data.

import httpx
from utils import get_url
import logging

logger = logging.getLogger(__name__)


class Bank:
    def __init__(self, slots, gold, inventory):
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
        url, headers = get_url(action="bank_details")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url, headers=headers)
                data = response.json()["data"]
                return data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while fetching bank details: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Network error while fetching bank details: {e}")
        except KeyError:
            logger.error("Malformed response: 'data' key missing in response")
        except Exception as e:
            logger.exception(f"Unexpected error while fetching bank details: {e}")
        return None

    @classmethod
    async def get_bank_items(cls):
        url, headers = get_url(action="bank_items")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url, headers=headers)
                data = response.json()["data"]
                return data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while fetching bank details: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Network error while fetching bank details: {e}")
        except KeyError:
            logger.error("Malformed response: 'data' key missing in response")
        except Exception as e:
            logger.exception(f"Unexpected error while fetching bank details: {e}")
        return None
