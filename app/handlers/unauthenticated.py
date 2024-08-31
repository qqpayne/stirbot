from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram_dialog import DialogManager, ShowMode, StartMode

from app import dialogs
from app.config import settings
from app.database import Database
from app.dialogs import setup_signup_dialog
from app.filters import NotAUserFilter
from app.strings import (
    NOT_A_USER_ERROR_TEXT,
    SIGNUP_TEXT,
)
from app.utils.admin import get_admin_link
from app.utils.user import register_new_user

router = Router(name="unauthenticated")
router.message.filter(NotAUserFilter())
router.callback_query.filter(NotAUserFilter())

setup_signup_dialog(router)


if settings.REQUEST_USER_ADDITIONALS:

    @router.message(CommandStart())
    async def start_handler(message: types.Message, dialog_manager: DialogManager) -> None:  # noqa: ARG001
        """
        Начинает с пользователем диалог для регистрации с запросом дополнительной информации.
        """
        await dialog_manager.start(dialogs.SignupFSM.main, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)


elif settings.USE_AUTHENTICATION:

    @router.message(CommandStart())
    async def start_handler(message: types.Message, db: Database) -> None:
        """
        Добавляет пользователя в базу данных и отправляет его писать администратору для подтверждения аккаунта.
        """
        if message.from_user is None:
            await message.answer(NOT_A_USER_ERROR_TEXT)
            return

        await register_new_user(db, message.from_user, approve=False)
        await message.answer(SIGNUP_TEXT.format(admin_link=await get_admin_link(db)))

else:

    @router.message(CommandStart())
    async def start_handler(message: types.Message, db: Database, dialog_manager: DialogManager) -> None:
        """
        Добавляет пользователя в базу данных, подтверждает его аккаунт и выводит главное меню.
        """
        if message.from_user is None:
            await message.answer(NOT_A_USER_ERROR_TEXT)
            return

        new_user = await register_new_user(db, message.from_user, approve=True)
        # user_data передается в диалоговый менеджер так как этот запрос не проходил через аутентификационный фильтр
        # добавляющий user_data, а эти данные необходимы для логики диалога (например, в is_admin)
        await dialog_manager.start(
            dialogs.UserFSM.main, data={"user_data": new_user}, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND
        )
