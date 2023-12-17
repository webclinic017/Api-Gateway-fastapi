import contextlib
from typing import TypeVar, Type, Dict, Any, List, Union

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_, exc, func

from .BaseSchemas import PaginationSchema
from core.bases import Base, CONNECTION_DATABASE



ModelType = TypeVar("ModelType", bound=Base)
RequestSchemaType = TypeVar("RequestSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)

class BaseRepository:
    """
        Base class for performing CRUD (Create, Read, Update, Delete, and List) 
        operations asynchronously with SQLAlchemy.
    """

    model: Type[ModelType] = None
    request_schema: Type[RequestSchemaType] = None
    response_schema: Type[RequestSchemaType] = None

    @contextlib.asynccontextmanager
    async def get_connection(self) -> AsyncSession:
        """
            Obtains a connection to the database.
        """
        async with CONNECTION_DATABASE.SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()


    async def create(self, schema: RequestSchemaType, **kwargs: Dict[str, Any]) -> ResponseSchemaType:
        """
            Creates a new object in the database.

            Args:
                schema: A Pydantic object containing the data to insert.
                **kwargs: Additional arguments to create the object.

            Returns:
                A Pydantic object created from the SQLAlchemy object created in the database.
        """
        async with self.get_connection() as session:
            async with session.begin():
                object = self.model(**schema.model_dump(exclude_unset=True), **kwargs)
                session.add(object)
                await session.commit()

                result = await self.get(id=object.id)
            
            return self.response_schema.model_validate(obj=result, from_attributes=True)


    async def update(self, schema: RequestSchemaType, **kwargs: Dict[int, Any]) -> ResponseSchemaType:
        """
            Updates an existing object in the database.

            Args:
                schema: A Pydantic object containing the data to update.
                **kwargs: Arguments to filter the object to update.

            Returns:
                An updated Pydantic object.
        """
        async with self.get_connection() as session:
            async with session.begin():
                statement = update(self.model).filter_by(**kwargs).values(**schema.model_dump(exclude_unset=True))
                await session.execute(statement)
    
                object = await session.execute(select(self.model).filter_by(**kwargs))

                return self.response_schema.model_validate(obj=object.scalar_one(), from_attributes=True)


    async def delete(self, **kwargs: Dict[int, Any]) -> None:
        """
            Deletes an object from the database.

            Args:
                **kwargs: Arguments to filter the object to delete.
        """
        async with self.get_connection() as session:
            async with session.begin():
                statement = self.model.__table__.delete().where(
                    *[(getattr(self.model, key) == value) for key, value in kwargs.items()]
                )
                await session.execute(statement)
                await session.commit()


    async def filter(self, **kwargs: Dict[int, Any]) -> List[ResponseSchemaType]:
        """
            Filters objects in the database based on certain criteria.

            Args:
                **kwargs: Arguments to filter the objects.

            Returns:
                A list of Pydantic objects that meet the filtering criteria.
        """
        async with self.get_connection() as session:
            async with session.begin():
                statement = select(self.model).filter_by(**kwargs)
                result = await session.execute(statement)
                return [self.response_schema.model_validate(obj=object, from_attributes=True) for object in result.scalars()]


    async def get(self, **kwargs: Dict[int, Any]) -> ResponseSchemaType:
        """
            Gets an object from the database based on certain criteria.

            Args:
                **kwargs: Arguments to search for the object.

            Returns:
                A Pydantic object found in the database.
        """
        async with self.get_connection() as session:
            async with session.begin():
                statement = select(self.model).filter_by(**kwargs)
            
                try:
                    data = await session.execute(statement)
                    result = data.scalar_one()
                    return self.response_schema.model_validate(obj=result, from_attributes=True)
            
                except exc.NoResultFound:
                    return None


    async def count_records(self, session: CONNECTION_DATABASE, query) -> int:
        """
            Counts the number of records in a query.

            Args:
                session: The SQLAlchemy session in which the query will be executed.
                query: The SQL query to count.

            Returns:
                The number of records.
        """
        result = await session.execute(select(func.count()).select_from(query.subquery()))
        return result.scalar()


    async def list(
        self,
        page_number: int,
        page_size: int,
        search: Union[str, None] = None,
        search_fields: List[str] = [],
    ) -> PaginationSchema:
        """
            Lists objects from the database with pagination and search options.

            Args:
                page_number: Page number.
                page_size: Page size.
                search: Search term (optional).
                search_fields: List of field names where the search will be performed (optional).

            Returns:
                A dictionary with pagination information and page content.
        """
        async with self.get_connection() as session:
            # Create a single transaction for all operations
            async with session.begin():
                query = select(self.model)

                if search and search_fields:
                    # Apply search on specified fields
                    filters = []
                    for field in search_fields:
                        filters.append(getattr(self.model, field).ilike(f"%{search}%"))
                    query = query.filter(or_(*filters))

                # Calculate pagination limits
                total_record = await self.count_records(session, query)
                total_pages = (total_record + page_size - 1) // page_size

                # Apply pagination
                offset = max((page_number - 1), 0) * page_size
                query = query.limit(page_size).offset(offset)

                # Execute the query and get results
                result = await session.execute(query)
                content = [self.response_schema.model_validate(obj=object, from_attributes=True) for object in result.scalars()]

                return PaginationSchema(
                    page_number=page_number,
                    page_size=page_size,
                    total_pages=total_pages,
                    total_record=total_record,
                    content=content
                )