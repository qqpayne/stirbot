from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage

from app.config import settings

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# настройка KeyBuilder нужна для aiogram-dialog
storage = RedisStorage.from_url(settings.redis_url, key_builder=DefaultKeyBuilder(with_destiny=True))
dp = Dispatcher(storage=storage)
