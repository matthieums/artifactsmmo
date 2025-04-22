import logging

API_KEY='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Im1hcnRlbnMubWF0dGhpZXVAaG90bWFpbC5jb20iLCJwYXNzd29yZF9jaGFuZ2VkIjoiIn0.ARDWMe5_tUvMPvrrNR_-tuSAOcr1EWOPruhYFj3u_FY'


def setup_logging():
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%H:%M:%S"
    )

    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
