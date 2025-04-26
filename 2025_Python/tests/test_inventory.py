import pytest
from errors import InventoryFullError, ItemNotFoundError


# --------------------
# inventory.add()
# --------------------
@pytest.mark.asyncio
async def test_add_existing_item(inventory_factory):
    inventory = inventory_factory({"apple": 5}, max_capacity=10)
    inventory.add("apple", 2)
    assert inventory.get("apple") == 7


@pytest.mark.asyncio
async def test_add_new_item(inventory_factory):
    inventory = inventory_factory({"sword": 2}, max_capacity=10)
    inventory.add("apple", 2)
    assert inventory.get("apple") == 2


@pytest.mark.asyncio
async def test_add_too_many_items(inventory_factory):
    inventory = inventory_factory({"sword": 2}, max_capacity=5)
    with pytest.raises(InventoryFullError):
        inventory.add("sword", 5)


# --------------------
# inventory.remove()
# --------------------
@pytest.mark.asyncio
async def test_remove_valid_item_quantity(inventory_factory):
    inventory = inventory_factory({"apple": 5})
    inventory.remove("apple", 3)
    assert inventory.get("apple") == 2


@pytest.mark.asyncio
async def test_remove_all_items(inventory_factory):
    inventory = inventory_factory({"apple": 5})
    inventory.remove("apple")
    assert inventory.get("apple") == 0


@pytest.mark.asyncio
async def test_remove_excessive_amount(inventory_factory):
    inventory = inventory_factory({"apple": 5})
    inventory.remove("apple", 10)
    assert inventory.get("apple") == 0


@pytest.mark.asyncio
async def test_remove_non_existent_item(inventory_factory):
    inventory = inventory_factory({"sword": 5})
    with pytest.raises(ItemNotFoundError):
        inventory.remove("apple", 5)
