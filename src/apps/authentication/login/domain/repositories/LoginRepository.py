from typing import Dict

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.databases.Models import Users
from core.bases.BaseRepositories import BaseRepository
from Gateway.src.apps.authentication.login.domain.schemas.LoginSchema import LoginRequestSchema
from Gateway.src.apps.authentication.register.domain.schemas.RegisterSchema import RegisterRequestSchema
from core.databases.Models import (
    Users,
    Systems,
    Endpoints
)



class LoginRepository(BaseRepository):
    model = Users
    request_schema = LoginRequestSchema
    response_schema = RegisterRequestSchema

            
    async def get_user_data(self, user_email: int) -> Dict:
        async with self.get_connection() as session:
            async with session.begin():

                # Obtener el usuario con el ID proporcionado
                statement = select(Users).where(Users.email == user_email).options(
                    selectinload(Users.roles),
                    selectinload(Users.groups),
                    selectinload(Users.systems),
                )
                user = await session.execute(statement)
                user = user.scalar()

                if user:
                    # Extraer roles, grupos y sistemas
                    roles = [{"role_name": role.role_name} for role in user.roles]
                    groups = [{"group_name": group.group_name} for group in user.groups]
                    systems = [{"name_system": system.name_system, "system_code": system.system_code} for system in user.systems]

                    # Construir el diccionario de resultado
                    result = {
                        "id": user.id,
                        "email": user.email,
                        "password": user.password,
                        "is_active": user.is_active,
                        "is_superuser": user.is_superuser,
                        "roles": roles,
                        "groups": groups,
                        "systems": systems
                    }
        
                else:
                    result = {}

            return result


    async def get_endpoints_by_system_code(self, system_code: str) -> Dict:
        async with self.get_connection() as session:
            async with session.begin():

                # Obtener el sistema con el código proporcionado
                statement = select(Systems).where(Systems.system_code == system_code)
                system = await session.execute(statement)
                system = system.scalar()

                if not system:
                    return {"endpoints": []}

                # Obtener todos los endpoints asociados con ese sistema
                statement = select(Endpoints).join(Endpoints.endpoint_microservice).filter(Systems.id == system.id).options(
                    selectinload(Endpoints.roles),
                    selectinload(Endpoints.groups),
                )
                endpoints = await session.execute(statement)
                endpoints = endpoints.scalars().all()

                # Convertir a la estructura deseada
                result = [
                    {
                        'endpoint_name': endpoint.endpoint_name,
                        'endpoint_url': endpoint.endpoint_url,
                        'system_code': endpoint.endpoint_microservice.microservice_system.system_code,
                        'roles': [role.role_name for role in endpoint.roles],
                        'groups': [group.group_name for group in endpoint.groups]
                    }
                    for endpoint in endpoints
                ]

            return {"endpoints": result}



LOGIN_REPOSITORY = LoginRepository()