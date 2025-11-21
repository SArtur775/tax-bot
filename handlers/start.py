# handlers/start.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.reply import get_main_menu

start_router = Router()

@start_router.message(Command("start"))
async def cmd_start(message: Message):
    # Первое сообщение - заголовок
    await message.answer("🎯 <b>Главное меню</b>")
    
    # Второе сообщение - кнопки
    await message.answer(
        "Выберите раздел:",
        reply_markup=get_main_menu()
    )

# Добавляем обработчик для команды /menu
@start_router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("🎯 <b>Главное меню</b>")
    await message.answer(
        "Выберите раздел:",
        reply_markup=get_main_menu()
    )