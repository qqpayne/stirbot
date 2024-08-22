from aiogram import Dispatcher

from .database import DatabaseMiddleware
from .scheduler import SchedulerMiddleware
from app.database.loader import sessionmaker
from app.utils.scheduler import scheduler


def setup(dp: Dispatcher) -> None:
    dp.update.middleware(DatabaseMiddleware(sessionmaker=sessionmaker))
    dp.update.middleware(SchedulerMiddleware(scheduler=scheduler))
