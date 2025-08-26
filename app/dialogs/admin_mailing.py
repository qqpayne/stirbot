from typing import Any

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Group, Next
from aiogram_dialog.widgets.text import Const
from loguru import logger

from app.database import Database
from app.strings import (
    BACK_TEXT,
    SEND_MASS_MESSAGE_CONFIRM_BUTTON_TEXT,
    SEND_MASS_MESSAGE_CONFIRMATION_TEXT,
    SEND_MASS_MESSAGE_INPUT_TEXT,
)
from app.utils.admin import send_mass_message


class AdminMessageFSM(StatesGroup):
    enter_message = State()
    confirm_send = State()


async def on_confirm_send(callback: CallbackQuery, _: Any, manager: DialogManager) -> None:  # noqa: ANN401
    db: Database = manager.middleware_data["db"]
    text: str = manager.find("text_input").get_value()  # pyright: ignore[reportOptionalMemberAccess]
    assert isinstance(db, Database)  # noqa: S101
    assert isinstance(text, str)  # noqa: S101
    logger.info(f"Admin with tg_id:{callback.from_user.id} initiated mass mailing")
    await send_mass_message(db, text)
    await manager.done()


admin_mailing_dialog = Dialog(
    Window(
        Const(SEND_MASS_MESSAGE_INPUT_TEXT),
        TextInput(
            id="text_input",
            type_factory=str,
            on_success=Next(),
            on_error=Cancel(),
        ),
        Cancel(Const(BACK_TEXT)),
        state=AdminMessageFSM.enter_message,
    ),
    Window(
        Const(SEND_MASS_MESSAGE_CONFIRMATION_TEXT),
        Group(
            Button(Const(SEND_MASS_MESSAGE_CONFIRM_BUTTON_TEXT), id="confirm_send", on_click=on_confirm_send),
            Back(Const(BACK_TEXT)),
            width=2,
        ),
        state=AdminMessageFSM.confirm_send,
    ),
)
