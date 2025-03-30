import asyncio
import logging

from aiogram import Bot, Dispatcher

from core.config import BOT_API_TOKEN
from handlers import base


async def main() -> None:
    bot = Bot(token=BOT_API_TOKEN)
    dp = Dispatcher()

    dp.include_router(base.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        filename="cca_bot.log",
        level=logging.INFO,
    )
    asyncio.run(main())
