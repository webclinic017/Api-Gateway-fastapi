from fastapi import FastAPI

from apps.gateway.routers import gateway
from apps.authentication.routers import authentication



def routersApp(app: FastAPI) -> None:
    app.include_router(gateway)
    app.include_router(authentication)