from core.databases.Models import Users
from core.bases.BaseRepositories import BaseRepository
from apps.authentication.register.domain.entities.RegisterEntity import (
    RegisterRequestEntity,
    RegisterResponseEntity
)



class RegisterRepository(BaseRepository):
    model = Users
    request_schema = RegisterRequestEntity
    response_schema = RegisterResponseEntity


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