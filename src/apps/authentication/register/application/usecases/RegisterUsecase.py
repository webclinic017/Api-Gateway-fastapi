from typing import Any

from fastapi import HTTPException, status

from core.helpers.HasingHelper import HASHING
from apps.authentication.register.domain.schemas.RegisterSchema import RegisterRequestSchema
from apps.authentication.register.domain.repositories.RegisterRepository import REGISTER_REPOSITORY



class RegisterUsecase:

    @staticmethod
    async def register(register: RegisterRequestSchema) -> Any:
        
        if await REGISTER_REPOSITORY.filter(email=register.email):
            """ Verificara la existencia del correo electronico """

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST, 
                detail = {
                    "code":status.HTTP_400_BAD_REQUEST, 
                    "message":f"El correo [{register.email}], ya existe."
                }
            )

        #### SETEA EL password Y SETEA A NONE EL password_repeat
        #### ANTES DEL INSERT EN LA DB
        register.password: str = await HASHING.hash_password(register.password)
        response = await REGISTER_REPOSITORY.register_user(
            email=register.email,
            password=register.password
        )
        return response
    


REGISTER_USECASES = RegisterUsecase()