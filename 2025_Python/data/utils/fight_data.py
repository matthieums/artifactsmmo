
from __future__ import annotations
import logging
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.character import Character

from utils.feedback import format_loot_message
logger = logging.getLogger(__name__)


async def handle_fight_data(character: Character, response) -> None:
    logger.info("handling fight data...")

    data = response.json()
    fight_data = data['data']['fight']
    loot = {}

    logger.info(f"{character} won the fight")

    if fight_data.get("gold"):
        gold = fight_data["gold"]
        character.update_gold(gold)
        loot["gold"] = gold

    if fight_data.get("drops"):
        items = defaultdict(int)
        for item in fight_data["drops"]:
            code, qty = item.get("code"), item.get("quantity")
            character.update_inventory(code, qty)
            items[code] += qty
        loot["items"] = items

    if fight_data.get("xp"):
        loot["xp"] = fight_data.get("xp")

    character.update_hp(data["data"]["character"]["hp"])

    format_loot_message(character.name, loot)

    return