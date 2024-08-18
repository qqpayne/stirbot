import zoneinfo

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BotSettings(EnvBaseSettings):
    BOT_TOKEN: str
    TIMEZONE: str

    @field_validator("TIMEZONE")
    @classmethod
    def timezone_should_be_available(cls, v: str) -> str:
        if v not in zoneinfo.available_timezones():
            msg = f"{v} timezone is not available, check zoneinfo.available_timezones() for available timezones"
            raise ValueError(msg)
        return v

    @property
    def tz(self) -> zoneinfo.ZoneInfo:
        return zoneinfo.ZoneInfo(self.TIMEZONE)


class DBSettings(EnvBaseSettings):
    POSTGRES_SERVER: str = "postgres:5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str = "postgres"

    @property
    def database_url(self) -> URL | str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"


class RedisSettings(EnvBaseSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


class Settings(BotSettings, DBSettings, RedisSettings):
    DEBUG: bool = False


settings = Settings()  # type: ignore  # noqa: PGH003
