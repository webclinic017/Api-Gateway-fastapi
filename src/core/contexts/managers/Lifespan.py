from contextlib import asynccontextmanager

from fastapi import FastAPI

from settings import SETTINGS
from core.bases import CONNECTION_DATABASE



@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """
        Asynchronous context manager for handling the 
        lifespan of a FastAPI application.

        Args:
            app (FastAPI): The FastAPI application instance.

        Yields:
            None
    """
    if SETTINGS.EXISTS_TABLES:
        await CONNECTION_DATABASE.create_all()

    yield

    await CONNECTION_DATABASE.close()