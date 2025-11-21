# handlers/start.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.reply import get_main_menu
from config import db  # Импортируем базу данных из config.py

start_router = Router()

@start_router.message(Command("start"))
async def cmd_start(message: Message):
    # Сохраняем/получаем пользователя в базе
    user = await db.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Первое сообщение - заголовок
    await message.answer("🎯 <b>Главное меню</b>")
    
    # Второе сообщение - кнопки
    await message.answer(
        "Выберите раздел:",
        reply_markup=get_main_menu()
    )

@start_router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("🎯 <b>Главное меню</b>")
    await message.answer(
        "Выберите раздел:",
        reply_markup=get_main_menu()
    )