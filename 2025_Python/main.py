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
        await hero.fight('cows')
        # monster = "chicken"
        # asyncio.run(hero.fight(monster))
        return

if __name__ == "__main__":
    asyncio.run(create_instance())