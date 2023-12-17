from fastapi import APIRouter

from apps.authentication.login.interfaces.controllers.LoginController import login_router
from apps.authentication.register.interfaces.controllers.RegisterController import register_router



authentication = APIRouter(prefix="/authentication", tags=["Authentication"])
authentication.include_router(login_router)
authentication.include_router(register_router)