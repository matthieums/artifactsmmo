import asyncio
import httpx
from models import Character
import config
from utils import get_url

######### This is where the process starts and makes calls to create the characters and distribute tasks


async def run_character_loop(iterations: int | None, character, method_name: str, *args, **kwargs):

    method = getattr(character, method_name)

    if not callable(method):
        raise AttributeError(f"'{method_name} is not a valid method")

    if iterations is None:
        while True:
            await method(*args, **kwargs)
    elif isinstance(iterations, int):
        for _ in range(iterations):
            await method(*args, **kwargs)
    else:
        raise ValueError("Iterations must be an int or None")


async def create_instance():
    url, headers = get_url(action="char_data")

    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)
        data = response.json()["data"]
        characters = [Character.from_api_data(entry) for entry in data]

        g = "gather"
        d= "deposit"
        w = "withdraw"
        f = "fight"
        c_r = "copper_rocks"
        a_w = "ash_wood"
        a_t = "ash_tree"
        c = "chickens"
        r = "rest"

        # For individual commands
        # await asyncio.gather(
        #     run_character_loop(characters[0], g, location=c_r),
        #     run_character_loop(characters[1], g, location=c_r),
        #     run_character_loop(characters[2], g, location=c_r),
        #     run_character_loop(characters[3], g, location=c_r),
        #     run_character_loop(characters[4], g, location=c_r),
        # )


        # When I need everyone to do the same thing
        tasks = []
        for i in range(len(characters)):
            tasks.append(run_character_loop(None, characters[i], g, location=c_r))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(create_instance())
