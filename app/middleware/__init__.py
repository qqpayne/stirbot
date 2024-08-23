from aiogram import Dispatcher

from .database import DatabaseMiddleware
from app.database.loader import sessionmaker


def setup(dp: Dispatcher) -> None:
    dp.update.middleware(DatabaseMiddleware(sessionmaker=sessionmaker))
