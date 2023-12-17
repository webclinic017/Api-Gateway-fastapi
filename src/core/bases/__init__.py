from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from settings import SETTINGS


class Base(DeclarativeBase):
    """
        Base class for SQLAlchemy declarative statements.
    """
    pass


class AsyncDatabaseSession:
    """
        Class providing an interface for working with asynchronous SQLAlchemy database sessions.

        Attributes:
            url (str): The URL of the database to connect to.
            engine (AsyncEngine): The SQLAlchemy engine for the database.
            SessionLocal (sessionmaker): The SQLAlchemy session generator.
            session (AsyncSession): The active session.
    """


    def __init__(self, url: str = SETTINGS.DATABASE_URL) -> None:
        """
            Initializes an instance of AsyncDatabaseSession.

            Args:
                url (str, optional): The database URL (default is the configuration URL).
        """
        self.engine: AsyncEngine = create_async_engine(url, echo=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )


    async def create_all(self) -> None:
        """
            Creates all tables defined in the model in the database.
        """
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)


    async def close(self) -> None:
        """
            Closes the database connection.
        """
        await self.engine.dispose()


    async def __aenter__(self) -> AsyncSession:
        """
            Initiates a new session and returns it.

            Returns:
                AsyncSession: The active session.
        """
        self.session: AsyncSession = self.SessionLocal()
        return self.session


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
            Closes the session when used in an 'async with' context.
        """
        await self.session.close()


    async def commit_rollback(self) -> None:
        """
            Attempts to commit the current transaction, and if it fails, performs a rollback.
        """
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise



CONNECTION_DATABASE = AsyncDatabaseSession()
