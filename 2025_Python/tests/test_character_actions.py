
from models import Character
from unittest.mock import patch
import pytest


# command to run = PYTHONPATH=2025_Python pytest 2025_Python/tests


@pytest.mark.asyncio
@patch("asyncio.sleep", return_value=None)
async def test_handle_cooldown(mock_sleep, test_character):
    character = test_character

    await character.handle_cooldown(5)

    mock_sleep.assert_called_once_with(5)
    assert character.cooldown_duration == 0


