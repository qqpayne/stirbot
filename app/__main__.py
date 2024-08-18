from typing import Any

import uvloop
from aiogram.filters import ExceptionTypeFilter
from aiogram_dialog import DialogManager, setup_dialogs
from aiogram_dialog.api.exceptions import UnknownState
from loguru import logger

from app import handlers, middleware
from app.loader import bot, dp
from app.utils import commands, logging


async def on_unknown_state(event: Any, dialog_manager: DialogManager) -> None:  # noqa: ARG001, ANN401
    logger.error("Restarting dialog")
    await dialog_manager.reset_stack()


async def on_startup() -> None:
    logger.info("Bot starting...")
    middleware.setup(dp)
    handlers.setup(dp)
    await commands.setup(bot)
    setup_dialogs(dp)
    dp.errors.register(on_unknown_state, ExceptionTypeFilter(UnknownState))
    logger.info("Bot started")


async def on_shutdown() -> None:
    logger.info("Bot stopping...")
    await dp.storage.close()
    await dp.fsm.storage.close()
    await bot.session.close()
    logger.info("Bot stopped")


async def main() -> None:
    logging.setup()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # type: ignore  # noqa: PGH003


if __name__ == "__main__":
    uvloop.run(main())
