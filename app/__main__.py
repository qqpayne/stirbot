import uvloop
from loguru import logger

from app import middleware
from app.loader import bot, dp
from app.utils import logging


async def main() -> None:
    logging.setup()
    logger.info("Bot started")
    middleware.setup(dp)
    await dp.start_polling(bot)  # type: ignore  # noqa: PGH003


if __name__ == "__main__":
    uvloop.run(main())
