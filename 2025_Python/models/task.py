import logging
logger = logging.getLogger(__name__)
import traceback
from dataclasses import dataclass, field
from typing import Callable, Any
import inspect


@dataclass
class Task:
    method: Callable[..., Any]
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)

    async def run(self):
        if callable(self.method):
            if inspect.iscoroutinefunction(self.method):
                return await self.method(*self.args, **self.kwargs)
            else:
                return self.method(*self.args, **self.kwargs)
        else:
            raise TypeError("Task is not callable")

    def log_success(self):
        logger.info("Task completed.")

    def __str__(self):
        return f"{self.kwargs['action']}"
