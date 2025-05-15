from collections import defaultdict, deque
import asyncio
import logging
import state
from models.task import Task
from models.character import Character
from .constants import WORKING, IDLE

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self):
        self.task_queues = defaultdict(deque)
        self.lock = asyncio.Lock()

    async def add_task(
        self,
        character: Character,
        method_name: str,
        iterations: int = 1,
        *args,
        **kwargs
    ) -> None:
        task = self._create_task(character, method_name, *args, **kwargs)
        async with self.lock:
            await self._enqueue_task(character, iterations, task)

    async def listen(self):
        logger.debug("Listener starting...")
        characters = state.characters.values()
        while True:
            for char in characters:
                if char.state == IDLE and self._has_tasks(char):
                    asyncio.create_task(self._run_queue(char))
            await asyncio.sleep(5)

    @staticmethod
    def _create_task(
        character: Character, method_name: str, *args, **kwargs
    ) -> Task:
        method = getattr(character, method_name)

        if not callable(method):
            raise AttributeError(f"'{method} is not a valid method")

        task = Task(method=method, args=args, kwargs=kwargs)
        logger.info(f"task created for {character}")
        return task

    async def _enqueue_task(
        self,
        character: Character,
        iterations: int,
        task: Task
    ) -> None:
        logger.debug("Enqueuing task")
        for _ in range(iterations):
            self.task_queues[character.name].append(task)
        logger.debug("Enqueued task")

    def _has_tasks(self, character: "Character"):
        return bool(self.task_queues[character.name])

    async def _run_queue(self, character: "Character"):
        name = character.name
        character.state = WORKING
        while self.task_queues[name]:
            async with self.lock:
                task = self.task_queues[name].popleft()
            await character.perform_task(task)
        character.state = IDLE
