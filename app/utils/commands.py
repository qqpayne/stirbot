from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from app.strings import commands


async def setup(bot: Bot) -> None:
    await remove(bot)

    # Админские команды тяжелее обновлять, будем предполагать что админы пользуются /help
    await bot.set_my_commands(
        [BotCommand(command=command, description=description) for command, description in commands.items()],
        scope=BotCommandScopeDefault(),
    )


async def remove(bot: Bot) -> None:
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
