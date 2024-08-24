from aiogram import Dispatcher

from .database import DatabaseMiddleware
from .user_consistency import UserConsistencyMiddleware
from app.database.loader import sessionmaker


def setup(dp: Dispatcher) -> None:
    dp.update.middleware(DatabaseMiddleware(sessionmaker=sessionmaker))
    dp.update.middleware(UserConsistencyMiddleware())
