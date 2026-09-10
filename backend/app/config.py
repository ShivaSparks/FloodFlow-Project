from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./floodflow_stage2.sqlite3"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    data_root: str = "./data/flood_project_data"
    processed_data_root: str = "./data/processed"
    source_crs: str = "EPSG:4326"
    target_crs: str = "EPSG:4326"
    pilot_south: float = 12.90
    pilot_north: float = 13.00
    pilot_west: float = 80.18
    pilot_east: float = 80.245
    demo_operator_email: str = "operator@example.com"
    demo_operator_password: str = "change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        value = str(value).strip().strip('"').strip("'")
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith(
            ("postgresql://", "postgresql+psycopg://")
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def secure_cookies(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
