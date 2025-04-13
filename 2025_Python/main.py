from models import Character
import asyncio
import httpx
import config


async def create_instance():
    url = "https://api.artifactsmmo.com/my/characters"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.API_KEY}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)
        data = response.json()
        char = data["data"][0]
        slot_keys = [
                "weapon_slot", "shield_slot", "helmet_slot", "body_armor_slot",
                "leg_armor_slot", "boots_slot", "ring1_slot", "ring2_slot",
                "amulet_slot", "artifact1_slot", "artifact2_slot", "artifact3_slot"
            ]
        hero = Character(
            name=char.get("name"),
            position=[char.get("x"), char.get("y")],
            equipment={slot: char.get(slot, "") for slot in slot_keys}
        )
        while True:
            await hero.gather(location="copper_rocks")


if __name__ == "__main__":
    asyncio.run(create_instance())