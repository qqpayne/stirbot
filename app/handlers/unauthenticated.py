from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram_dialog import DialogManager, ShowMode, StartMode
from loguru import logger

from app import dialogs
from app.config import settings
from app.database import Database
from app.dialogs import setup_signup_dialog
from app.filters import NotAUserFilter
from app.strings import (
    NOT_A_USER_ERROR_TEXT,
    SIGNUP_TEXT,
    SUGGEST_SIGNUP_TEXT,
    UNAUTH_CALLBACK_TEXT,
    UNKNOWN_USER_START_TEXT,
)
from app.utils.admin import get_admin_link
from app.utils.user import register_new_user

router = Router(name="unauthenticated")
router.message.filter(NotAUserFilter())
router.callback_query.filter(NotAUserFilter())

setup_signup_dialog(router)


if settings.USE_AUTHENTICATION:

    @router.message(CommandStart())
    async def start_handler(message: types.Message) -> None:
        """
        Приветствует пользователя и предлагает зарегистрироваться.
        """
        await message.answer(UNKNOWN_USER_START_TEXT)

    @router.message(Command("signup"))
    async def signup_handler(message: types.Message, db: Database, dialog_manager: DialogManager) -> None:
        """
        Добавляет пользователя в базу данных и отправляет его писать администратору для подтверждения аккаунта.
        """
        if settings.REQUEST_USER_ADDITIONALS:
            await dialog_manager.start(dialogs.SignupFSM.main, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)
        else:
            if message.from_user is None:
                await message.answer(NOT_A_USER_ERROR_TEXT)
                return

            await register_new_user(db, message.from_user, approve=False)
            await message.answer(SIGNUP_TEXT.format(admin_link=await get_admin_link(db)))

else:

    @router.message(CommandStart())
    async def start_handler(message: types.Message, db: Database, dialog_manager: DialogManager) -> None:
        """
        Добавляет пользователя в БД, подтверждает его аккаунт и выводит главное меню.
        """
        if settings.REQUEST_USER_ADDITIONALS:
            await dialog_manager.start(dialogs.SignupFSM.main, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)
        else:
            if message.from_user is None:
                await message.answer(NOT_A_USER_ERROR_TEXT)
                return

            new_user = await register_new_user(db, message.from_user, approve=True)
            # user_data передается в диалоговый менеджер так как этот запрос не проходил через аутентификационный фильтр
            # добавляющий user_data, а эти данные необходимы для логики диалога (например, в is_admin)
            await dialog_manager.start(
                dialogs.UserFSM.main, data={"user_data": new_user}, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND
            )


# Так как при REQUEST_USER_ADDITIONALS начинается диалог с интерактивным вводом и catch-all хэндлеры мешают диалогу
if not settings.REQUEST_USER_ADDITIONALS:

    @router.message()
    async def any_message_handler(message: types.Message) -> None:
        """
        Предлагает пользователю зарегистрироваться в ответ на любые сообщения.
        """
        await message.answer(SUGGEST_SIGNUP_TEXT)

    @router.callback_query()
    async def any_callback_handler(callback: types.CallbackQuery) -> None:
        """
        Предлагает пользователю зарегистрироваться в ответ на коллбэк.
        """
        if not isinstance(callback.message, types.Message):
            logger.error("Strange unauthenticated callback without message")
            return

        logger.warning(
            "Received unauthenticated callback from {user} id={user_id}",
            user=callback.from_user.full_name,
            user_id=callback.from_user.id,
        )
        await callback.message.edit_text(UNAUTH_CALLBACK_TEXT)
        await callback.message.answer(SUGGEST_SIGNUP_TEXT)
        await callback.answer()
