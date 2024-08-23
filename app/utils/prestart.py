import sys

import tenacity
import uvloop
from loguru import logger
from redis.asyncio.client import Redis
from sqlalchemy import text
from tenacity import after_log, before_log

from app.config import settings
from app.database.loader import sessionmaker

TIMEOUT_BETWEEN_ATTEMPTS = 2
MAX_TIMEOUT = 30


@tenacity.retry(
    wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
    stop=tenacity.stop_after_delay(MAX_TIMEOUT),
    before=before_log(logger, "INFO"),  # type: ignore[arg-type]
    after=after_log(logger, "WARNING"),  # type: ignore[arg-type]
)
async def wait_postgres() -> None:
    try:
        async with sessionmaker() as db:
            version = await db.execute(text("SELECT version();"))
            version_row = version.first()
            if version_row is not None:
                logger.info(f"Connected to {version_row[0]}")
    except Exception as e:
        logger.error(e)
        raise


@tenacity.retry(
    wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
    stop=tenacity.stop_after_delay(MAX_TIMEOUT),
    before=before_log(logger, "INFO"),  # type: ignore[arg-type]
    after=after_log(logger, "WARNING"),  # type: ignore[arg-type]
)
async def wait_redis() -> None:
    client = Redis.from_url(settings.redis_url)
    try:
        info = await client.info()
        logger.info("Connected to Redis server v{redis}", redis=info["redis_version"])
    except Exception as e:
        logger.error(e)
        raise
    finally:
        await client.aclose()  # type: ignore[attr-defined]


async def main() -> None:
    logger.info("Wait for PostgreSQL...")
    try:
        await wait_postgres()
    except tenacity.RetryError:
        logger.error("Failed to establish connection with PostgreSQL.")
        sys.exit(1)

    logger.info("Wait for RedisDB...")
    try:
        await wait_redis()
    except tenacity.RetryError:
        logger.error("Failed to establish connection with RedisDB.")
        sys.exit(1)

    logger.info("Prestart routine completed")


if __name__ == "__main__":
    uvloop.run(main())
