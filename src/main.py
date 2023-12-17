import core.utils.Logger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import SETTINGS
from core.routers.Routers import routersApp
from core.contexts.managers.Lifespan import lifespan
from core.middlewares.RateLimitMiddleware import RateLimitMiddleware



app = FastAPI(
    title=SETTINGS.PROJECT_NAME,
    openapi_url=f"{SETTINGS.URL_API_DOCUMENTATION}openapi.json",
    lifespan=lifespan
)


#### Middlewares
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#### Routers
routersApp(app=app)
