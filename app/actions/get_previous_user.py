import datetime as dt

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode

from .base import Action
from app.database import Database
from app.database.models import User
from app.loader import bot
from app.strings import (
    ERROR_TEXT,
    GET_PREVIOUS_USER_ACTION_ACCESS_ERROR_TEXT,
    GET_PREVIOUS_USER_ACTION_CONDITION_TEXT,
    GET_PREVIOUS_USER_ACTION_DESCRIPTION_TEXT,
    GET_PREVIOUS_USER_ACTION_NO_PREVIOUS_TEXT,
    GET_PREVIOUS_USER_ACTION_NOTIFY_TEXT,
    GET_PREVIOUS_USER_ACTION_RESULT_TEXT,
    GET_PREVIOUS_USER_ACTION_TITLE_TEXT,
    RETRY_ERROR_TEXT,
)


class GetPreviousUserAction(Action):
    @property
    def id(self) -> str:
        return "get_previous_user"

    @property
    def title(self) -> str:
        return GET_PREVIOUS_USER_ACTION_TITLE_TEXT

    @property
    def description(self) -> str:
        return GET_PREVIOUS_USER_ACTION_DESCRIPTION_TEXT

    @property
    def execution_conditions(self) -> str:
        return GET_PREVIOUS_USER_ACTION_CONDITION_TEXT

    def is_place_suitable(self, place: str) -> bool:  # noqa: ARG002
        return True

    async def can_execute(self, dialog_manager: DialogManager) -> bool:
        place_id: str = dialog_manager.dialog_data["place"]
        user: User = dialog_manager.middleware_data["user_data"]
        db: Database = dialog_manager.middleware_data["db"]
        assert isinstance(place_id, str)  # noqa: S101
        assert isinstance(user, User)  # noqa: S101
        assert isinstance(db, Database)  # noqa: S101

        ongoing_booking = await db.booking.get_user_ongoing_in_place(user.id, place_id)
        return ongoing_booking is not None

    # TODO: strings.py
    async def __call__(self, callback_query: CallbackQuery, dialog_manager: DialogManager) -> None:  # noqa: ARG002
        place_id: str = dialog_manager.dialog_data["place"]
        user: User = dialog_manager.middleware_data["user_data"]
        db: Database = dialog_manager.middleware_data["db"]
        assert isinstance(place_id, str)  # noqa: S101
        assert isinstance(user, User)  # noqa: S101
        assert isinstance(db, Database)  # noqa: S101

        if not isinstance(callback_query.message, Message):
            await callback_query.answer(ERROR_TEXT.format(error=RETRY_ERROR_TEXT))
            return

        ongoing_booking = await db.booking.get_user_ongoing_in_place(user.id, place_id)
        if ongoing_booking is None:
            await callback_query.message.edit_text(ERROR_TEXT.format(error=GET_PREVIOUS_USER_ACTION_ACCESS_ERROR_TEXT))
            dialog_manager.show_mode = ShowMode.SEND
            return

        now = dt.datetime.now(dt.timezone.utc)
        already_ended_booking = [
            booking
            for booking in await db.booking.get_by_location(
                place_id, now.replace(hour=0, minute=0, second=0, microsecond=0)
            )
            if booking.end <= now
        ]
        already_ended_booking.sort(key=lambda booking: booking.end)
        if len(already_ended_booking) == 0:
            await callback_query.message.edit_text(GET_PREVIOUS_USER_ACTION_NO_PREVIOUS_TEXT)
            dialog_manager.show_mode = ShowMode.SEND
            return

        last_booking = already_ended_booking[-1]
        last_user = await last_booking.awaitable_attrs.user
        # У пользователя может быть не указан username или заблокированы сообщения от не-контактов.
        # Так что лучше отправить сообщение еще и тому, кого ищут
        await bot.send_message(
            last_user.id,
            GET_PREVIOUS_USER_ACTION_NOTIFY_TEXT.format(user=user.clickable_name, place=last_booking.place_id),
        )
        await callback_query.message.edit_text(
            GET_PREVIOUS_USER_ACTION_RESULT_TEXT.format(last_user=last_user.clickable_name)
        )
        dialog_manager.show_mode = ShowMode.SEND
