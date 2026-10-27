from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ACME Salary Management"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./salary.db"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    seed_on_startup: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
