from aiogram import Dispatcher
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from app.config import settings
from app.loader import bot

jobstores = {
    "default": RedisJobStore(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD)
}

executors = {"default": AsyncIOExecutor()}
job_defaults = {"coalesce": True, "max_instances": 3, "misfire_grace_time": 0}

scheduler = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=settings.tz)


async def on_startup() -> None:
    scheduler.start()


async def on_shutdown() -> None:
    scheduler.shutdown()


def setup(dp: Dispatcher) -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)


async def send_message_job(chat_id: int | str, message_text: str) -> None:
    logger.info(f"Sent scheduled message to {chat_id}")
    await bot.send_message(chat_id, message_text)
