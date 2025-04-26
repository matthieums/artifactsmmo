from utils import send_request


async def get_item_info(item: str) -> dict:
    response = await send_request(action="item_info", item=item)
    return response.json()
