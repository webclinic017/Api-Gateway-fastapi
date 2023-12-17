from typing import Union

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.future import select

from core.databases.Models import Users, Endpoints
from core.bases.BaseRepositories import BaseRepository
from core.helpers.JwtManagerHelper import JwtManagerHelper



class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False, scheme_name: str = "Authorization") -> None:
        super(JWTBearer, self).__init__(auto_error=auto_error, scheme_name=scheme_name)


    async def __call__(self, request: Request) -> Union[dict, HTTPException]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        base = BaseRepository()

        if credentials and not credentials.credentials == "null":
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "status": status.HTTP_403_FORBIDDEN, 
                        "message": "[1] Invalid or expired token."
                    }
                )

            jwt_token = await JwtManagerHelper(token=credentials.credentials).validate_token()

            if request.url.path.startswith("/administration/") and not request.url.path.startswith("/administration/users/get_current_user"):
                async with base.get_connection() as session:
                    async with session.begin():
                        user = await session.execute(
                            select(Users).where(Users.email == jwt_token.get("email"), Users.is_superuser == True)
                        )

                        if user.scalar() is None:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail={
                                    "status": status.HTTP_403_FORBIDDEN,
                                    "message": "[1] Access denied."
                                }
                            )
            
            # #######################################################
            # #### FUNCTIONALITY TO VERIFY THAT THE USER IS LOGGED IN
            # #### PLEASE MEET ALL REQUIREMENTS BEFORE ACCESSING
            # #### TO THE REQUESTED ROUTE
            from core.helpers.PermissionHelper import PERMISSION_HELPER

            async with base.get_connection() as session:
                async with session.begin():
                    user_id = (
                        await session.execute(
                            select(Users.id).where(Users.email == jwt_token.get("email"))
                        )
                    ).scalar()

                    control_access = await PERMISSION_HELPER.user_access_control(
                        user_id,            # ID OF THE LOGGED USER
                        request.url.path    # PATH TO THE PATH THE USER WANTS TO ACCESS
                    )

                    if control_access:
                        return jwt_token
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN, 
                            detail={
                                "status": status.HTTP_403_FORBIDDEN, 
                                "message": "[2] Access denied."
                            }
                        )

        else:
            if request.url.path in ["/authentication/login", "/authentication/register"]:
                return True

            async with base.get_connection() as session:
                async with session.begin():
                    endpoint = (
                        await session.execute(
                            select(Endpoints).where(
                                Endpoints.endpoint_url == request.url.path.replace("/gateway", ""),
                                Endpoints.endpoint_authenticated == False
                            )
                        )
                    ).scalar()

                    if endpoint:
                        return True

                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, 
                        detail={
                            "status": status.HTTP_403_FORBIDDEN, 
                            "message": "Not authenticated."
                        }
                    )


OAUTH2 = JWTBearer()
