from collections import defaultdict, deque
import asyncio
import logging
import state
from models.task import Task
from models.character import Character

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
        async with self.lock:
            task = self._create_task(character, method_name, *args, **kwargs)
            await self._enqueue_task(character, iterations, task)

    async def listen(self):
        try:
            characters = list(state.characters)
            logger.debug("Listener starting...")
            while True:
                await asyncio.sleep(5)
                if any(self._has_tasks(char) for char in characters):
                    async with self.lock:
                        logger.debug("Tasks detected")
                        await self._run_queues()
                        continue
                else:
                    logger.info("All queues are empty."
                                "waiting for new tasks to be added...")

        except Exception as e:
            raise Exception(f"{str(e)}")

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

    def _has_tasks(self, character_name):
        return bool(self.task_queues[character_name])

    async def _start_tasks(self, char_name: str):
        while self.task_queues[char_name]:
            task = self.task_queues[char_name].popleft()
            self.set_ongoing_task(char_name, task)
            logger.info(f"Running task for {char_name}: {task}")
            await task.run()

    async def _run_queues(self):
        async with asyncio.TaskGroup() as tg:
            for char_name in state.characters:
                if self._has_tasks(char_name):
                    logger.info(f"Found tasks for {char_name}, starting task group.")
                    tg.create_task(self._start_tasks(char_name))
                else:
                    logger.info(f"No tasks for {char_name}, skipping.")

    def set_ongoing_task(self, char_name: str, task: Task):
        state.characters[char_name].ongoing_task = str(task)
