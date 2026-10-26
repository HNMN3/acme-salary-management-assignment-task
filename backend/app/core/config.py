from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ACME Salary Management"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./salary.db"
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
