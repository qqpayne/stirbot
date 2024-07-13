from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BotSettings(EnvBaseSettings):
    BOT_TOKEN: str


class DBSettings(EnvBaseSettings):
    POSTGRES_SERVER: str = "postgres:5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str = "postgres"

    @property
    def database_url(self) -> URL | str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"


class Settings(BotSettings, DBSettings):
    DEBUG: bool = False


settings = Settings()  # type: ignore  # noqa: PGH003
