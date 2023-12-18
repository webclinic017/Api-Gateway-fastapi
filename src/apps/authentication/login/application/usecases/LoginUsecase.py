from typing import Union

from fastapi import HTTPException, status

from core.helpers.ItemHelper import ITEM_HELPER
from core.helpers.HasingHelper import HASHING
from core.helpers.JwtManagerHelper import JwtManagerHelper
from apps.authentication.login.domain.repositories.LoginRepository import LOGIN_REPOSITORY
from Gateway.src.apps.authentication.login.domain.schemas.LoginSchema import (
    LoginRequestSchema,
    LoginResponseSchema
)



class LoginUsecase:

    @staticmethod
    async def login(login: LoginRequestSchema) -> Union[LoginResponseSchema, HTTPException]:
        
        user = await LOGIN_REPOSITORY.get_user_data(user_email=login.email)

        if not user:
            """ Verificara la existencia del correo electronico """

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, 
                detail = {
                    "code":status.HTTP_404_NOT_FOUND, 
                    "message":f"El correo [{login.email}], no existe."
                }
            )

        if not await HASHING.verify_password(user["password"], login.password):
            """ Verificara la validez de la contraseña """
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, 
                detail = {
                    "code":status.HTTP_404_NOT_FOUND, 
                    "message":f"Contraseña incorrecta."
                }
            )

        #### Obtendra los sistemas del usuario
        from core.helpers.PermissionHelper import PERMISSION_HELPER
        user_systems = await PERMISSION_HELPER.get_user_systems(user["id"])

        if not login.system_code in user_systems and user["is_superuser"] == False:
                """ Si el usuario no tiene permisos al sistema donde quiere ingresar 
                y si no es un superusuario, enviará una excepción """
                raise HTTPException(
                    status_code = status.HTTP_403_FORBIDDEN, 
                    detail = {
                        "code":status.HTTP_403_FORBIDDEN, 
                        "message":"No tiene permisos para acceder al sistema, comuníquese con el área de soporte."
                    }
                )
    
        #### Obtendra los endpoints del sistema con los permisos
        endpoints = await LOGIN_REPOSITORY.get_endpoints_by_system_code(login.system_code)

        jwt = JwtManagerHelper(
            data = await ITEM_HELPER.remove_items(
                dictionary = {**user, **endpoints}, 
                items_to_remove = [
                    "password",
                ]
            )
        )

        return LoginResponseSchema(
            type = "Bearer",
            token = await jwt.create_token(),
            refresh_token = await jwt.refresh_token()
        )



LOGIN_USECASES = LoginUsecase()