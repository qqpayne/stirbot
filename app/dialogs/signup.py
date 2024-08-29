from typing import Any

from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button
from aiogram_dialog.widgets.text import Const, Format

from .user import UserFSM
from app.config import settings
from app.database import Database
from app.strings import (
    BACK_TEXT,
    SIGNUP_CONFIRM_BUTTON_TEXT,
    SIGNUP_CONFIRM_ECHO_TEXT,
    SIGNUP_CONFIRM_HELLO_TEXT,
    SIGNUP_TEXT,
)
from app.utils.admin import get_admin_link
from app.utils.user import register_new_user


class SignupFSM(StatesGroup):
    main = State()
    confirmation = State()


async def on_user_info_entered(_: Message, __: Any, manager: DialogManager, parsed_data: str) -> None:  # noqa: ANN401
    manager.dialog_data["user_additional"] = parsed_data
    await manager.switch_to(SignupFSM.confirmation)


async def on_confirmation(callback: CallbackQuery, _: Any, manager: DialogManager) -> None:  # noqa: ANN401
    db: Database = manager.middleware_data["db"]
    user_additional = manager.dialog_data["user_additional"]
    assert isinstance(db, Database)  # noqa: S101
    assert isinstance(user_additional, str)  # noqa: S101

    if settings.USE_AUTHENTICATION:
        new_user = await register_new_user(db, callback.from_user, approve=False, additional_info=user_additional)
        if not isinstance(callback.message, Message):
            await manager.switch_to(SignupFSM.main)
            return
        await callback.message.edit_text(SIGNUP_TEXT.format(admin_link=await get_admin_link(db)))
        await manager.done()
    else:
        new_user = await register_new_user(db, callback.from_user, approve=True, additional_info=user_additional)
        if isinstance(callback.message, Message):
            await callback.message.delete()
        await manager.start(
            UserFSM.main, data={"user_data": new_user}, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND
        )


signup_dialog = Dialog(
    Window(
        Const(SIGNUP_CONFIRM_HELLO_TEXT),
        TextInput(id="user_additional", on_success=on_user_info_entered),
        state=SignupFSM.main,
    ),
    Window(
        Format(SIGNUP_CONFIRM_ECHO_TEXT),
        Button(Const(SIGNUP_CONFIRM_BUTTON_TEXT), id="confirm", on_click=on_confirmation),
        Back(Const(BACK_TEXT)),
        state=SignupFSM.confirmation,
    ),
)


def setup_signup_dialog(router: Router) -> None:
    router.include_routers(signup_dialog)
