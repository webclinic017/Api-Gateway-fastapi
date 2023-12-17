from typing import List

from decouple import config
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings



class Settings(BaseSettings):

    # App config
    PROJECT_NAME: str = config("PROJECT_NAME", cast=str)
    URL_API_DOCUMENTATION: str = "/documentation/"
    EXISTS_TABLES: bool = False

    # Jwt auth config
    ALGORITHM: str = config("ALGORITHM", cast=str)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 60  # EXPIRES IN 1 HOUR
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # EXPIRES IN 7 DAYS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:4400"] # LIST OF URLS ALLOWED FOR ACCESS

    # Database config
    DATABASE_URL: str = config("DATABASE_URL", cast=str)

    # Vault config
    SYSTEM_CODE: str = config("SYSTEM_CODE", cast=str)
    VAULT_SECRET_KEY: str = config("VAULT_SECRET_KEY", cast=str)
    GRPC_SERVER_ADDRESS: str = config("GRPC_SERVER_ADDRESS", cast=str)

    # Rate limit config
    REQUESTS_PER_SECOND: int = 15 # MAXIMUM NUMBER OF REQUESTS ALLOWED PER SECOND
    REQUEST_INTERVAL: int = 1 # TIME INTERVAL IN SECONDS
    BLOCK_DURATION: int = 60 # LOCK TIME IN SECONDS

    class Config:
        case_sensitive = True



SETTINGS = Settings()