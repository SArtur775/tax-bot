# handlers/start.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.main_menu import get_main_menu

# Даем уникальное имя
start_router = Router()  # ← ИМЕННО ТАК!


@start_router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в <b>Налоговый помощник</b>!\n\n"
        "Я помогу вам разобраться с налогами:\n"
        "• 🔄 Рассчитать налоги\n"
        "• 💰 Вернуть налоговые вычеты\n" 
        "• 📅 Не пропустить сроки сдачи отчетности\n"
        "• 👤 Оптимизировать налоги для самозанятых\n"
        "• 🔔 Настроить напоминания\n\n"
        "Выберите раздел в меню ниже 👇",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )