import pytest
from errors import ItemNotCraftableError
from models import Item


# --------------------
# Item.from_data()
# --------------------
@pytest.mark.asyncio
async def test_item_from_data_craftable():
    data = {
        "name": "Iron Sword",
        "code": "iron_sword",
        "type": "weapon",
        "craft": {
            "skill": "weaponcrafting",
            "items": [{"code": "iron_ingot", "quantity": 2}]
        }
    }

    item = Item.from_data(data)

    assert item.name == "Iron Sword"
    assert item.code == "iron_sword"
    assert item.type == "weapon"
    assert item.craftable is True
    assert item.ingredients == [{"code": "iron_ingot", "quantity": 2}]
    assert item.skill == "weaponcrafting"

@pytest.mark.asyncio
async def test_item_from_data_non_craftable():
    data = {
        "name": "Ash_wood",
        "code": "ash_wood",
        "type": "resource",
    }

    item = Item.from_data(data)

    assert item.name == "Ash_wood"
    assert item.code == "ash_wood"
    assert item.type == "resource"
    assert item.craftable is False
    assert item.ingredients == []
    assert item.skill is None