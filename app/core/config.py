from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Letter API"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/letter"
    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 60 * 24 * 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
