from aiogram import Dispatcher

from . import authenticated, unauthenticated


def setup(dp: Dispatcher) -> None:
    # Порядок роутеров важен
    routers = [authenticated.router, unauthenticated.router]

    dp.include_routers(*routers)
