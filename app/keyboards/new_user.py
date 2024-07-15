from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NewUserAction(Enum):
    approve = "approve"
    deny = "deny"


class NewUserCBF(CallbackData, prefix="new_user"):
    action: NewUserAction
    id: int


def new_user_kb(uid: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Подтвердить", callback_data=NewUserCBF(action=NewUserAction.approve, id=uid))
    keyboard.button(text="❌ Отказать", callback_data=NewUserCBF(action=NewUserAction.deny, id=uid))
    keyboard.adjust(2)
    return keyboard.as_markup()
