from functools import wraps
from data import locations, bank_actions
import inspect

def check_character_position(f):
    """Wrapper that checks if character is in the correct position to make the
    requested action. If not, he is moved to the necessary position"""
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        required_position = kwargs.get("location")

        func_name = f.__name__
        if func_name in bank_actions:
            required_position = "bank"

        if not required_position:
            raise RuntimeError('Missing location')

        if self.position != locations[required_position]:
            await self.move_to(required_position)

        if inspect.iscoroutinefunction(f):
            return await f(self, *args, **kwargs)
        else:
            return f(self, *args, **kwargs)
    return wrapper
