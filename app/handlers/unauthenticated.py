from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from loguru import logger

from app.database import Database
from app.filters import NotAUserFilter
from app.strings import NOT_A_USER_ERROR_TEXT, SIGNUP_TEXT, SUGGEST_SIGNUP_TEXT, UNKNOWN_USER_START_TEXT
from app.utils.admin import get_admin_link

router = Router(name="unauthenticated")
router.message.filter(NotAUserFilter())


@router.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    """
    Приветствует пользователя и предлагает зарегистрироваться.
    """
    await message.answer(UNKNOWN_USER_START_TEXT)


@router.message(Command("signup"))
async def signup_handler(message: types.Message, db: Database) -> None:
    """
    Добавляет пользователя в базу данных и отправляет его писать администратору для подтверждения аккаунта.
    """
    if message.from_user is None:
        await message.answer(NOT_A_USER_ERROR_TEXT)
        return

    # Авторизованные пользователи не должны попадать в этот хэндлер, можно не проверять отсутствие пользователя в базе
    new_user = await db.user.create(message.from_user)
    logger.info("New user registered: {user}", user=new_user)

    await message.answer(SIGNUP_TEXT.format(admin_link=await get_admin_link(db)))


@router.message()
async def any_message_handler(message: types.Message) -> None:
    """
    Предлагает пользователю зарегистрироваться в ответ на любые сообщения.
    """
    await message.answer(SUGGEST_SIGNUP_TEXT)
