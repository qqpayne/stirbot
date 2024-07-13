import sys

import tenacity
import uvloop
from loguru import logger
from sqlalchemy import text
from tenacity import after_log, before_log

from app.database.loader import sessionmaker

TIMEOUT_BETWEEN_ATTEMPTS = 2
MAX_TIMEOUT = 30


@tenacity.retry(
    wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
    stop=tenacity.stop_after_delay(MAX_TIMEOUT),
    before=before_log(logger, "INFO"),  # type: ignore  # noqa: PGH003
    after=after_log(logger, "WARNING"),  # type: ignore  # noqa: PGH003
)
async def wait_postgres() -> None:
    async with sessionmaker() as db:
        version = await db.execute(text("SELECT version();"))
        version_row = version.first()
        if version_row is not None:
            logger.info(f"Connected to {version_row[0]}")


async def main() -> None:
    logger.info("Wait for PostgreSQL...")
    try:
        await wait_postgres()
    except tenacity.RetryError:
        logger.error("Failed to establish connection with PostgreSQL.")
        sys.exit(1)

    logger.info("Prestart routine completed")


if __name__ == "__main__":
    uvloop.run(main())
