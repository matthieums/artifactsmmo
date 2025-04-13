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
        hero = Character(char["name"], [char["x"], char["y"]])
        # while True:
            # await hero.gather('ash_tree')
        await hero.craft("wooden_staff")
        # await hero.craft('wooden_stick')

        return

if __name__ == "__main__":
    asyncio.run(create_instance())