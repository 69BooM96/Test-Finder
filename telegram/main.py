import asyncio

from aiogram import Bot, Dispatcher

from app.handlers import router
from config import TOKEN


async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher(bot)

    dp.include_router(router)
    
    print("BOT START")

    dp.start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyError:
        print("BOT OFF")