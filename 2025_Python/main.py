from models import Character
import asyncio
import httpx
import config


async def run_character_loop(char_data, method_name, *args, **kwargs):
    slot_keys = [
        "weapon_slot", "shield_slot", "helmet_slot", "body_armor_slot",
        "leg_armor_slot", "boots_slot", "ring1_slot", "ring2_slot",
        "amulet_slot", "artifact1_slot", "artifact2_slot", "artifact3_slot"
    ]

    character = Character(
        name=char_data.get("name"),
        position=[char_data.get("x"), char_data.get("y")],
        equipment={slot: char_data.get(slot, "") for slot in slot_keys},
        inventory={item["code"]: item["quantity"] for item in char_data["inventory"] if item["quantity"] > 0}
    )

    method = getattr(character, method_name)

    while True:
        await method(*args, **kwargs)


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

        arthur = data["data"][0]
        guenievre = data["data"][1]
        lancelot = data["data"][2]
        percival = data["data"][3]
        morgan = data["data"][4]

        await asyncio.gather(
            run_character_loop(arthur, "gather", location="copper_rocks"),
            run_character_loop(guenievre, "gather", location="copper_rocks"),
            run_character_loop(lancelot, "gather", location="copper_rocks"),
            run_character_loop(percival, "gather", location="copper_rocks"),
            run_character_loop(morgan, "gather", location="copper_rocks"),
        )

if __name__ == "__main__":
    asyncio.run(create_instance())