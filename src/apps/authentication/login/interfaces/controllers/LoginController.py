from fastapi import APIRouter, status

from core.bases.BaseSchemas import ResponseSchema
from apps.authentication.login.domain.entities.LoginEntity import LoginRequestEntity
from apps.authentication.login.application.usecases.LoginUsecase import LOGIN_USECASES



login_router = APIRouter()

@login_router.post("/login", response_model=ResponseSchema, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def login(request: LoginRequestEntity):
    return ResponseSchema(
        status = status.HTTP_200_OK, 
        detail = "Se inició sesión correctamente.",
        result = await LOGIN_USECASES.login(request)
    )