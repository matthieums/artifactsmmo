from models import Character
from unittest.mock import patch, MagicMock
import pytest


# command to run = PYTHONPATH=2025_Python pytest 2025_Python/tests
# Must be called from artifactsmmo folder !!!


############## character.handle_cooldown
@pytest.mark.asyncio
@patch("asyncio.sleep", return_value=None)
async def test_handle_cooldown(mock_sleep, test_character):
    """Checks if the function properly calls sleep and reduce 
    the character's cooldown duration to 0"""
    character = test_character

    await character.handle_cooldown(5)

    mock_sleep.assert_called_once_with(5)
    assert character.cooldown_duration == 0


############## character.gather()
@pytest.mark.asyncio
@patch("models.character.post_character_action")
@patch("models.character.Character.update_inventory")
@patch("models.character.Character.handle_cooldown")
async def test_gather_success(mock_handle_cooldown, mock_update_inventory, mock_post_character_action, test_character):
    """Checks if a 2xx response triggers the appropriate functions"""
    character = test_character
    mock_response = MagicMock()
    mock_response.is_success = True
    item = {"code": "test_item", "quantity": "1"}
    mock_response.json.return_value = {
        "data": {
            "details": {
                "items": [item]
            },
            "cooldown": {"total_seconds": 5}
        }
    }

    location = "test_location"
    gather = "gather"

    mock_post_character_action.return_value.is_success = True
    mock_post_character_action.return_value = mock_response

    character.position = location

    await character.gather(location=location)
    mock_post_character_action.assert_called_once_with(test_character.name, gather, location)
    mock_update_inventory.assert_called_once_with(action=gather, item=item)
    mock_handle_cooldown.assert_called_once_with(5)


@pytest.mark.asyncio
@patch("models.character.post_character_action")
@patch("models.character.Character.update_inventory")
@patch("models.character.Character.handle_cooldown")
async def test_gather_failure(mock_handle_cooldown, mock_update_inventory, mock_post_character_action, test_character):
    """Checks if 4xx http responses trigger exception"""
    character = test_character
    mock_post_character_action.side_effect = Exception("Failed to send post request")

    location = "test_location"
    gather = "gather"
    character.position = location
    result = await character.gather(location=location)

    assert result == 0
    mock_post_character_action.assert_called_once_with(character.name, gather, location)
    mock_handle_cooldown.assert_not_called()
    mock_update_inventory.assert_not_called()


@pytest.mark.asyncio
@patch("models.character.post_character_action")
async def test_gather_inventory_full(mock_post_character_action, test_character):
    """Checks if inventory full returns 1"""
    character = test_character
    location = "test_location"
    character.position = location

    mock_response = MagicMock()
    mock_response.is_success = False
    mock_response.status_code = 497
    mock_post_character_action.return_value = mock_response

    result = await character.gather(location=location)
    assert result == 1
