import uvloop
from aiogram_dialog import setup_dialogs
from loguru import logger

from app import handlers, middleware
from app.loader import bot, dp
from app.utils import commands, errors, logging, scheduler


async def on_startup() -> None:
    logger.info("Bot starting...")
    middleware.setup(dp)
    handlers.setup(dp)
    await commands.setup(bot)
    setup_dialogs(dp)
    errors.setup(dp)
    logger.info("Bot started")


async def on_shutdown() -> None:
    logger.info("Bot stopping...")
    await dp.storage.close()
    await dp.fsm.storage.close()
    await bot.session.close()
    logger.info("Bot stopped")


async def main() -> None:
    logging.setup()
    scheduler.setup(dp)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # type: ignore  # noqa: PGH003


if __name__ == "__main__":
    uvloop.run(main())
