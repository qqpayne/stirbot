from typing import Any

from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group
from aiogram_dialog.widgets.text import Const
from loguru import logger

from app.database import Database
from app.strings import APPROVE_USERS_BUTTON_TEXT, BACK_TEXT, USE_MENU_BUTTONS_TEXT
from app.utils.admin import list_new_users


class AdminFSM(StatesGroup):
    main = State()


async def on_approve_users(callback: CallbackQuery, _: Any, manager: DialogManager) -> None:  # noqa: ANN401
    db = manager.middleware_data["db"]
    message = callback.message
    assert isinstance(db, Database)  # noqa: S101

    if not isinstance(message, Message):
        logger.error("Strange callback without message")
        return

    await list_new_users(message, db)


admin_dialog = Dialog(
    Window(
        Const(USE_MENU_BUTTONS_TEXT),
        Group(Button(Const(APPROVE_USERS_BUTTON_TEXT), id="approve_users", on_click=on_approve_users), width=2),
        Cancel(Const(BACK_TEXT)),
        state=AdminFSM.main,
    ),
)


def setup_admin_dialog(router: Router) -> None:
    router.include_routers(admin_dialog)
