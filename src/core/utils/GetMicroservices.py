from fastapi import HTTPException

from sqlalchemy import exc
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from core.bases.BaseRepositories import BaseRepository
from core.databases.Models import Endpoints, MicroServices



async def get_microservices(path: str):
    """
        Retrieves the microservices based on the provided path.

        Args:
        - path (str): The path to the endpoint.

        Returns:
        - List of microservices.

        Raises:
        - HTTPException: If there are no available microservices for the endpoint.
    """
    base = BaseRepository()

    async with base.get_connection() as session:
        async with session.begin():
            statement = select(MicroServices).options(
                selectinload(MicroServices.back_endpoints_endpoint_microservice)
            ).where(
                MicroServices.back_endpoints_endpoint_microservice.has(Endpoints.endpoint_microservice == None) | 
                MicroServices.back_endpoints_endpoint_microservice.has(Endpoints.endpoint_url == path)
            )

            try:
                result = await session.execute(statement)
                microservices = result.scalar_one()
                return microservices.microservice_base_url

            except exc.NoResultFound:
                raise HTTPException(status_code=502, detail="No microservices available for this endpoint.")
