from collections import defaultdict, deque
import asyncio
import logging
import state

from models.task import Task
from models.character import Character

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self):
        self.task_queue = defaultdict(deque)

    @staticmethod
    def create_task(
        character: Character, method_name: str, *args, **kwargs
    ) -> Task:
        method = getattr(character, method_name)

        if not callable(method):
            raise AttributeError(f"'{method} is not a valid method")

        task = Task(method=method, args=args, kwargs=kwargs)
        logger.info(f"task created for {character}")
        return task

    def enqueue_task(self, character: Character, iterations: int, task: Task) -> None:
        for _ in range(iterations):
            self.task_queue[character].append(task)

    def add_task(self, iterations: int, character: Character, method_name: str, *args, **kwargs) -> None:
        task = self.create_task(character, method_name, *args, **kwargs)
        self.enqueue_task(character, iterations, task)

    async def start_tasks(self, character: Character):
        while self.task_queue[character]:
            task = self.task_queue[character].popleft()
            self.set_ongoing_task(character, task)
            await task.run()

    def set_ongoing_task(self, character: Character, task: Task):
        logger.debug(f"Dictionary: '{state.characters}'")
        logger.debug(f"Accessing character: '{character}'")
        state.characters[str(character)].ongoing_task = str(task)
        logger.debug(f"ONGOING TASK FOR {character} => {task}")

    async def run_queues(self, characters: list):
        async with asyncio.TaskGroup() as tg:
            for char in characters:
                tg.create_task(self.start_tasks(char))
