import uvloop
from aiogram import types
from aiogram.filters import ExceptionTypeFilter
from aiogram_dialog import DialogManager, setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from loguru import logger

from app import handlers, middleware
from app.loader import bot, dp
from app.strings import DIALOG_MANAGER_ERROR_TEXT, ERROR_TEXT
from app.utils import commands, logging


async def on_dialog_manager_error(event: types.ErrorEvent, dialog_manager: DialogManager) -> None:  # noqa: ARG001, ANN401
    logger.error(f"Restarting dialog: {event.exception}")
    await dialog_manager.reset_stack()
    if event.update.message is not None:
        await event.update.message.answer(ERROR_TEXT.format(error=DIALOG_MANAGER_ERROR_TEXT))
    elif (event.update.callback_query is not None) and isinstance(event.update.callback_query.message, types.Message):
        await event.update.callback_query.message.answer(ERROR_TEXT.format(error=DIALOG_MANAGER_ERROR_TEXT))


async def on_startup() -> None:
    logger.info("Bot starting...")
    middleware.setup(dp)
    handlers.setup(dp)
    await commands.setup(bot)
    setup_dialogs(dp)
    dp.errors.register(on_dialog_manager_error, ExceptionTypeFilter(UnknownState))
    dp.errors.register(on_dialog_manager_error, ExceptionTypeFilter(UnknownIntent))
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
