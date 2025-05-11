import logging
from dotenv import load_dotenv
import os
from api.server import app
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

API_KEY = os.getenv("API_KEY")

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%H:%M:%S"
    )

    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def setup_CORS():
    logger.info("Setup CORS")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
