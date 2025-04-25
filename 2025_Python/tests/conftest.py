from models import Character
from main import initialize_characters
import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def test_character():
    characters = await initialize_characters()
    return characters[0]
