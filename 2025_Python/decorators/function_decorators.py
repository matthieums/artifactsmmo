from functools import wraps
from utils.helpers import find_on_map
from data import locations, bank_actions
import inspect
import logging

logger = logging.getLogger(__name__)


def check_character_position(f):
    """Wrapper that checks if character is in the correct position to make the
    requested action. If not, he is moved to the necessary position"""
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        logger.info("Wrapper function called")

        if kwargs.get("resource"):
            resource = kwargs.get("resource")
            kwargs["location"] = await find_on_map(resource)
            logger.info(f"Resource found. Location set to {kwargs['location']}.")

        required_position = kwargs.get("location")

        func_name = f.__name__

        if func_name in bank_actions:
            required_position = "bank"

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
