from models import Character, Inventory, Item
from main import initialize_characters
import pytest
import pytest_asyncio
from datetime import datetime


@pytest_asyncio.fixture
async def test_character():
    characters = await initialize_characters()
    character = characters[0]
    character.cooldown_duration = 0
    character.cooldown_expiration = datetime.now(tz=None)
    return character


@pytest_asyncio.fixture
def inventory_factory(test_character):
    def create_inventory(slots, max_capacity: int = 50):
        return Inventory(character=test_character, slots=slots, max_capacity=max_capacity)
    return create_inventory

