import uvloop
from loguru import logger

from .utils import logging
from app.loader import bot, dp


async def main() -> None:
    logging.setup()
    logger.info("Bot started")
    await dp.start_polling(bot)  # type: ignore  # noqa: PGH003


if __name__ == "__main__":
    uvloop.run(main())
