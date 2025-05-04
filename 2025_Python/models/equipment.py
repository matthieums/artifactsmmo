import logging
from utils.requests_factory import send_request
from models.item import Item

logger = logging.getLogger(__name__)


class Equipment():
    SLOTS = [
        "weapon",
        "rune",
        "shield",
        "helmet",
        "body_armor",
        "leg_armor",
        "boots",
        "ring1",
        "ring2",
        "amulet",
        "artifact1",
        "artifact2",
        "artifact3",
        "utility1",
        "utility1_quantity",
        "utility2",
        "utility2_quantity",
        "bag",
    ]

    def __init__(self, **kwargs):
        for slot in self.SLOTS:
            setattr(self, slot, kwargs.get(slot, None))

    @classmethod
    def from_data(cls, data):
        slots = {slot: data.get(f"{slot}_slot") for slot in cls.SLOTS if not slot.endswith("_quantity")}
        slots["utility1_quantity"] = data.get("utility1_slot_quantity")
        slots["utility2_quantity"] = data.get("utility2_slot_quantity")
        return cls(**slots)

    async def equip(self, character, item: Item):
        action = "equip"
        slot_name = item.type
        code = item.code
        bank = character.bank

        if slot_name not in self.SLOTS:
            logger.error(f"This item type cannot be equipped: {item} - {item.type}")
            return

        if item not in character.inventory:
            async with bank.lock:
                try:
                    if code in bank:
                        await bank.reserve(character, {code: 1})
                        await bank.withdraw(character, code, 1)
                    else:
                        logger.error("Item was not found in inventory nor the bank.")
                except Exception as e:
                    logger.exception(f"an error occured {str(e)}")

        equipped_item = getattr(self, slot_name)

        item = str(item)

        if equipped_item:
            equipped_item = await Item.load(equipped_item)
            if code == equipped_item.code:
                logger.error("Item already equipped")
                return
            else:
                try:
                    await self.unequip(character, equipped_item.code)
                except Exception as e:
                    logger.error(f"Could not unequip {equipped_item.code}. Equip "
                                 f"action aborted. {str(e)}")
                    return

        try:
            response = await send_request(character=character.name, action=action, item=code, slot=slot_name)
            data = response.json()
        except Exception as e:
            logger.error(f"Error in equip method: {str(e)}")
            return 1
        else:
            setattr(self, slot_name, code)
            character.update_inventory(equipped_item, 1)
            character.update_inventory(code, -1)
            logger.info(f"{code} equipped in {slot_name} slot")
            await character.handle_cooldown(data["data"]["cooldown"]["total_seconds"])
            return

    async def unequip(self, character, item_code):
        item = await Item.load(item_code)
        action = "unequip"
        slot_name = item.type

        if slot_name not in self.SLOTS:
            logger.info(f"{item.type} is not a valid equipment slot")
            return

        equipped_item = getattr(self, slot_name)
        equipped_item = await Item.load(equipped_item)

        if equipped_item.code != item_code:
            logger.error("Cannot unequip an item that is not equipped")
            raise Exception

        try:
            response = await send_request(character=character.name, action=action, item=item_code, slot=slot_name)
            data = response.json()
        except Exception as e:
            logger.error(f"Error in fight method: {str(e)}")
            return 1
        else:
            setattr(self, slot_name, None)
            character.update_inventory(item_code, 1)
            logger.info(f"Unequipped {item_code} from {slot_name} and returned it to inventory.")
            await character.handle_cooldown(data["data"]["cooldown"]["total_seconds"])

    def __repr__(self):
        equipped = {slot: getattr(self, slot) for slot in self.SLOTS if getattr(self, slot)}
        return f"{equipped}"

    def __contains__(self, item):
        return item in self.slots.values()
