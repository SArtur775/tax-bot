# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv

from handlers.start import start_router
from handlers.main_menu import menu_router
from handlers.calculators.ndfl_calc import ndfl_router  
from handlers.calculators.usn6_calc import usn6_router 
from handlers.calculators.usn15_calc import usn15_router 

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(ndfl_router)
dp.include_router(usn6_router)
dp.include_router(usn15_router)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())