import asyncio
import logging

from aiogram import Bot, Dispatcher

from core.config import BOT_API_TOKEN, DATABASE_PATH
from core.logging import LoggerConfig
from data.factory import StorageFactory
from data.manager import DataManager
from handlers.base import setup_handlers


async def main() -> None:
    bot = Bot(token=BOT_API_TOKEN)
    dp = Dispatcher()

    storage = StorageFactory.create_storage(
        "sqlite",
        db_path=DATABASE_PATH,
    )
    data_manager = DataManager(storage)

    dp.include_router(setup_handlers(data_manager))

    logger.info("Бот запущен")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    logger = LoggerConfig(
        logger_name="main",
        log_file="cca_bot.log",
        log_level=logging.INFO,
        console_output=True
    ).get_logger()

    asyncio.run(main())
