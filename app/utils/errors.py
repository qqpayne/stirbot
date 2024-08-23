from aiogram import Dispatcher, types
from aiogram.exceptions import TelegramForbiddenError, TelegramServerError
from aiogram.filters import ExceptionTypeFilter
from aiogram_dialog import DialogManager
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from loguru import logger

from app.strings import DIALOG_MANAGER_ERROR_TEXT, ERROR_TEXT


async def on_dialog_manager_error(event: types.ErrorEvent, dialog_manager: DialogManager) -> None:
    logger.error(f"Restarting dialog: {event.exception}")
    await dialog_manager.reset_stack()
    if event.update.message is not None:
        await event.update.message.answer(ERROR_TEXT.format(error=DIALOG_MANAGER_ERROR_TEXT))
    elif (event.update.callback_query is not None) and isinstance(event.update.callback_query.message, types.Message):
        await event.update.callback_query.message.answer(ERROR_TEXT.format(error=DIALOG_MANAGER_ERROR_TEXT))


async def on_telegram_sourced_error(event: types.ErrorEvent) -> None:
    logger.error(f"Telegram error: {event.exception}")


def setup(dp: Dispatcher) -> None:
    dp.errors.register(on_dialog_manager_error, ExceptionTypeFilter(UnknownState))
    dp.errors.register(on_dialog_manager_error, ExceptionTypeFilter(UnknownIntent))
    dp.errors.register(on_telegram_sourced_error, ExceptionTypeFilter(TelegramForbiddenError))
    dp.errors.register(on_telegram_sourced_error, ExceptionTypeFilter(TelegramServerError))
