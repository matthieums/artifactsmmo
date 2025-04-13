from functools import wraps
import asyncio


def check_character_position(f):
    """Wrapper that checks if character is in the correct position to make the
    requested action. If not, he is moved to the necessary position"""
    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        if args:
            required_position = args[-1]

            if self.position != required_position:
                await self.move_to(required_position)

            return f(self, *args, **kwargs)
        else:
            raise RuntimeError
    return wrapper
