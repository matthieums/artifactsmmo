import logging
logger = logging.getLogger(__name__)


class Task:
    def __init__(self, method: callable, iterations: int | None, *args, **kwargs):
        if not callable(method):
            raise ValueError("Method is not callable")
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.iterations = iterations
        self.completed = False

    async def run(self):
        if self.iterations:
            try:
                for _ in range(self.iterations):
                    await self.method(*self.args, **self.kwargs)
                self.completed = True
                self.log_success()
                return 1
            except Exception as e:
                print(f"Exception occurred during task.run(): {e}")
                return

        while not self.completed:
            try:
                res = await self.method(*self.args, **self.kwargs)
                if res == 1:
                    self.completed = True
                    self.log_success()
                    return 1
            except Exception as e:
                print(f"Exception occurred during task.run(): {e!r}")
                return
        return

    def log_success(self):
        logger.info("Task completed.")

    def __str__(self):
        return f"{self.kwargs['action']}"
