import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties

from src.config import settings
from src.handlers import register_handlers
from src.service import randomize_gifts
from src.models import *
from src.database import Base


commands = [
    types.BotCommand(command="/start", description="Начать"),
    types.BotCommand(command="/menu", description="Меню"),
]


async def main() -> None:
    # await randomize_gifts()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()
    print("Бот запущен!")

    register_handlers(dp)

    await bot.set_my_commands(commands)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
