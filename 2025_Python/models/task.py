class Task:
    def __init__(self, method: callable, iterations: int | None, *args, **kwargs):
        if not callable(method):
            raise ValueError("Method is not callable")
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.iterations = iterations

    async def run(self):
        if self.iterations:
            for _ in range(self.iterations + 1):
                await self.method(*self.args, **self.kwargs)
        else:
            while True:
                await self.method(*self.args, **self.kwargs)
