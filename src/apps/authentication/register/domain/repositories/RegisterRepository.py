from core.databases.Models import Users
from core.bases.BaseRepositories import BaseRepository
from Gateway.src.apps.authentication.register.domain.schemas.RegisterSchema import (
    RegisterRequestSchema,
    RegisterResponseSchema
)



class RegisterRepository(BaseRepository):
    model = Users
    request_schema = RegisterRequestSchema
    response_schema = RegisterResponseSchema


    async def register_user(
        self, 
        email: str, 
        password: str
    ) -> None:
        async with self.get_connection() as session:
            async with session.begin():
                object = self.model(email=email, password=password)
                session.add(object)
                await session.commit()
    
            return self.response_schema.model_validate(obj=object, from_attributes=True)



REGISTER_REPOSITORY = RegisterRepository()