from fastapi import APIRouter, status

from core.bases.BaseSchemas import ResponseSchema
from Gateway.src.apps.authentication.register.domain.schemas.RegisterSchema import RegisterRequestSchema
from apps.authentication.register.application.usecases.RegisterUsecase import REGISTER_USECASES



register_router = APIRouter()

@register_router.post("/register", response_model=ResponseSchema, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequestSchema):
    return ResponseSchema(
        status = status.HTTP_201_CREATED, 
        detail = "El usuario fue registrado exitosamente.",
        result = await REGISTER_USECASES.register(request)
    )