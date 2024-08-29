from typing import Any

from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, DialogManager, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Cancel, Group, Start
from aiogram_dialog.widgets.text import Const, Format

from app.database import Database
from app.database.models import User
from app.dialogs.admin import AdminFSM
from app.dialogs.booking import BookingFSM, setup_booking_dialog
from app.dialogs.notifications import NotificationFSM, setup_notifications_dialog
from app.strings import (
    ADMIN_MENU_BUTTON_TEXT,
    BACK_TEXT,
    BOOKING_MENU_BUTTON_TEXT,
    FEEDBACK_MENU_BUTTON_TEXT,
    NOTIFICATIONS_MENU_BUTTON_TEXT,
    REPORT_TEXT,
    RULES_MENU_BUTTON_TEXT,
    RULES_TEXT,
    USE_MENU_BUTTONS_TEXT,
)
from app.utils.admin import get_admin_link


class UserFSM(StatesGroup):
    main = State()


class RulesFSM(StatesGroup):
    main = State()


class ReportFSM(StatesGroup):
    main = State()


async def admin_link_getter(db: Database, **_: dict[str, Any]) -> dict[str, str]:
    return {"admin_link": await get_admin_link(db)}


def is_admin(data: dict[str, Any], widget: Any, dialog_manager: DialogManager) -> bool:  # noqa: ANN401, ARG001
    user = data["middleware_data"]["user_data"]
    assert isinstance(user, User)  # noqa: S101
    return user.is_admin


async def rewrite_user_data(_: dict[str, Any], dialog_manager: DialogManager) -> None:
    """
    Хук, перехватывающий 'user_data' в 'start_data' диалогового мэнеджера и переписывающий данные в 'middleware_data'.
    Необходимо для возможности начать диалог не из под аутентификационного фильтра.
    """
    if dialog_manager.start_data is not None and "user_data" in dialog_manager.start_data:  # type: ignore[reportUnnecessaryComparison]
        user_data = dialog_manager.start_data.pop("user_data")
        dialog_manager.middleware_data["user_data"] = user_data


rules_dialog = Dialog(Window(Const(RULES_TEXT), Cancel(Const(BACK_TEXT)), state=RulesFSM.main))
report_dialog = Dialog(
    Window(Format(REPORT_TEXT), Cancel(Const(BACK_TEXT)), getter=admin_link_getter, state=ReportFSM.main)
)

user_dialog = Dialog(
    Window(
        Const(USE_MENU_BUTTONS_TEXT),
        Group(
            Start(text=Const(BOOKING_MENU_BUTTON_TEXT), id="booking", state=BookingFSM.main),
            Start(text=Const(NOTIFICATIONS_MENU_BUTTON_TEXT), id="notifications", state=NotificationFSM.main),
            Start(text=Const(RULES_MENU_BUTTON_TEXT), id="rules", state=RulesFSM.main),
            Start(text=Const(FEEDBACK_MENU_BUTTON_TEXT), id="feedbak", state=ReportFSM.main),
            # NOTE: получить доступ к первому окну AdminFSM можно подделав коллбэк и не обладая админскими привелегиями
            # но все последующие коллбэки будут отклонены фильтром в handlers/authenticated/admin
            Start(text=Const(ADMIN_MENU_BUTTON_TEXT), id="admin", state=AdminFSM.main, when=is_admin),
            width=2,
        ),
        state=UserFSM.main,
    ),
    on_start=rewrite_user_data,
    launch_mode=LaunchMode.ROOT,
)


def setup_user_dialog(router: Router) -> None:
    router.include_routers(user_dialog, rules_dialog, report_dialog)
    setup_booking_dialog(router)
    setup_notifications_dialog(router)
