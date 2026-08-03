from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Flight Menu API"
    app_env: str = "dev"
    debug: bool = True
    api_prefix: str = "/api/v1"
    app_port: int = 8000

    db_host: str = "localhost"
    db_port: int = 5435
    db_name: str = "flight_menu"
    db_username: str = "flight_menu"
    db_password: str = "flight_menu"
    db_pool_size: int = 10
    db_max_overflow: int = 10
    db_pool_timeout: float = 30.0

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    auth_username: str = "admin"
    auth_password: str = "admin"

    log_level: str = "INFO"
    # JSON for CloudWatch; console-friendly output when false (local dev)
    log_json: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
