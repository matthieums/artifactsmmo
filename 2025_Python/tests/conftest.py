from models import Character
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
