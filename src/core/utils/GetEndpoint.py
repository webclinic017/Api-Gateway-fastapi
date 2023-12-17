from fastapi import HTTPException

from sqlalchemy.future import select

from core.databases.Models import Endpoints
from core.bases.BaseRepositories import BaseRepository



async def get_endpoint(path: str):
    """
        Retrieves an endpoint based on the provided path.

        Args:
        - path (str): The path to the endpoint.

        Returns:
        - Endpoint object.

        Raises:
        - HTTPException: If the endpoint does not exist.
    """
    base = BaseRepository()

    async with base.get_connection() as session:
        async with session.begin():
            statement = select(Endpoints).where(Endpoints.endpoint_url == path)
            result = await session.execute(statement)
            endpoint = result.scalars().first()

            if endpoint is None:
                raise HTTPException(status_code=404, detail="The requested endpoint was not found.")
            
            return endpoint
