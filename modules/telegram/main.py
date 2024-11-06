import asyncio

from aiogram import Bot, Dispatcher

from app.handlers import router
from config import TOKEN


async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    print("BOT START")

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyError:
        print("BOT OFF")