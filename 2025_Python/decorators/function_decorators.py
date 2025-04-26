from functools import wraps
from data import locations, bank_actions
from utils import get_item_info
import inspect
import logging


logger = logging.getLogger(__name__)


def check_character_position(f):
    """Wrapper that checks if character is in the correct position to make the
    requested action. If not, he is moved to the necessary position"""
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        logger.info("Wrapper function called")
        required_position = kwargs.get("location")

        func_name = f.__name__

        if func_name in bank_actions:
            required_position = "bank"

        elif func_name == "craft":
            item_data = await get_item_info(*args)
            required_position = item_data["data"]["craft"]["skill"]

        if not required_position:
            logger.error("Triggered missing location error")
            raise RuntimeError('Missing location')

        if self.position != locations[required_position]:
            await self.move_to(required_position)

        if inspect.iscoroutinefunction(f):
            return await f(self, *args, **kwargs)
        else:
            return f(self, *args, **kwargs)
    return wrapper
