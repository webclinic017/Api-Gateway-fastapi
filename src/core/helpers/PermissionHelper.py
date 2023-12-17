from datetime import date
from typing import List, Optional, Union, Set

from fastapi import Depends, HTTPException, status

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from core.middlewares.JwtMiddleware import OAUTH2
from core.bases.BaseRepositories import BaseRepository
from core.databases.Models import Users, Roles, Groups, Systems, Endpoints



# ================================== USER ENTITY ==================================#
class RolesResponseEntity(BaseModel):
    id: int
    role_name: str

class GroupsResponseEntity(BaseModel):
    id: int
    group_name: str

class SystemsResponseEntity(BaseModel):
    id: int
    name_system: str

class ProfileResponseEntity(BaseModel):
    id: int
    first_name: str
    last_name: str
    document: str
    birth_date: date

class UserResponseEntity(BaseModel):
    id: int
    email: str
    is_active: bool

    roles: Optional[List[RolesResponseEntity]] = []
    groups: Optional[List[GroupsResponseEntity]] = []
    systems: Optional[List[SystemsResponseEntity]] = []
    profile: Optional[ProfileResponseEntity] = {}

# ================================== PERMISSION HELPER ==================================#
class PermissionHelper(BaseRepository):


    async def get_current_user(
        self,
        token: str = Depends(OAUTH2)
    ) -> Union[UserResponseEntity, bool]:
        """
            Obtains details of the current user from the token. If the requested endpoint does not require authentication,
            returns True.

            Args:
                token (str): Token for user authentication.

            Returns:
                Union[UserResponseEntity, bool]: User details or True.
        """
        if token is True:
            return True

        async with self.get_connection() as session:
            async with session.begin():
                user_data = await session.execute(select(Users).where(Users.email == token.get("email")))
                user = user_data.scalar()

                if user:
                    return UserResponseEntity.model_validate(obj=user, from_attributes=True)


    async def get_user_roles(self, user_id: str) -> Set[str]:
        """
            Obtains all roles of the user.

            Args:
                user_id (str): User ID.

            Returns:
                Set[str]: Set of roles.
        """
        async with self.get_connection() as session:
            async with session.begin():
                roles = await session.execute(
                    select(Roles.role_name).join(Users, Users.id == user_id)
                )
                return set(role for role, in roles.scalars())


    async def get_user_groups(self, user_id: str) -> Set[str]:
        """
            Obtains all groups of the user and their roles.

            Args:
                user_id (str): User ID.

            Returns:
                Set[str]: Set of roles.
        """
        async with self.get_connection() as session:
            async with session.begin():
                groups = await session.execute(
                    select(Groups).join(Users, Users.id == user_id).options(joinedload(Groups.roles))
                )
                return set(role.role_name for group in groups.scalars() for role in group.roles)


    async def get_endpoint_roles(self, path: str) -> Set[str]:
        """
            Obtains all roles associated with a specific endpoint.

            Args:
                path (str): Endpoint path.

            Returns:
                Set[str]: Set of roles.
        """
        async with self.get_connection() as session:
            async with session.begin():
                endpoint = await session.execute(select(Endpoints).where(Endpoints.endpoint_url == path).options(joinedload(Endpoints.roles)))
                if endpoint:
                    return set(role.role_name for role in endpoint.scalar().roles)
                else:
                    return set()


    async def get_endpoint_groups(self, path: str) -> Set[str]:
        """
            Obtains all roles associated with the group of a specific endpoint.

            Args:
                path (str): Endpoint path.

            Returns:
                Set[str]: Set of roles.
        """
        async with self.get_connection() as session:
            async with session.begin():
                endpoint_id = await session.execute(select(Endpoints.id).where(Endpoints.endpoint_url == path))
                groups = await session.execute(
                    select(Groups).join(Groups, Groups.endpoints_group_id == endpoint_id.scalar())
                )
                return set(role.role_name for group in groups.scalars() for role in group.roles)


    async def get_user_systems(self, user_id: str) -> Set[str]:
        """
            Obtains all systems associated with a specific user.

            Args:
                user_id (str): User ID.

            Returns:
                Set[str]: Set of systems.
        """
        async with self.get_connection() as session:
            async with session.begin():
                user_systems = await session.execute(
                    select(Systems).join(Users.systems).where(Users.id == user_id)
                )

                systems = user_systems.scalars().all()

                if systems:
                    return set(system.system_code for system in systems)
                else:
                    return set()


    async def get_microservice_systems(self, path: str) -> Set[str]:
        """
            Obtains the system from the path.

            Args:
                path (str): Endpoint path.

            Returns:
                Set[str]: Set of systems.
        """
        async with self.get_connection() as session:
            async with session.begin():
                systems = await session.execute(
                    select(Systems.system_code).join(Endpoints, Systems.microservices_systems.any(Endpoints.endpoint_url == path))
                )
                return set(system for system, in systems.scalars())


    async def user_access_control(self, user_id: int, path: str) -> bool:
        """
            Validates the access control of a user to a protected route.

            Args:
                user_id (int): User ID.
                path (str): Endpoint path.

            Returns:
                bool: True if the user has access, False otherwise.
        """
        if path in ["/administration/users/get_current_user", "/authentication/renew/token", "/authentication/keys/public_key"]:
            return True

        async with self.get_connection() as session:
            async with session.begin():
                user = await session.execute(
                    select(Users).filter((Users.id == user_id) & (Users.is_active == True) & (Users.is_superuser == True))
                )
                if user.scalar():
                    return True

                endpoint = await session.execute(select(Endpoints.endpoint_url).where(Endpoints.endpoint_url == path.replace("/gateway", "")))
                if not endpoint.scalar():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={"message": "Endpoint not found."}
                    )

        user_systems = await self.get_user_systems(user_id)

        if not user_systems:
            return False

        microservice_system = await self.get_microservice_systems(path)

        if user_systems & microservice_system:
            user_roles = await self.get_user_roles(user_id)
            user_groups = await self.get_user_groups(user_id)
            endpoint_roles = await self.get_endpoint_roles(path)
            endpoint_groups = await self.get_endpoint_groups(path)

            if not (endpoint_roles or endpoint_groups):
                return True

            return bool((user_roles | user_groups) & (endpoint_roles | endpoint_groups))

        return False



PERMISSION_HELPER = PermissionHelper()
