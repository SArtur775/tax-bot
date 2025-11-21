# handlers/main_menu.py
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_calculators_menu, get_main_menu
from handlers.comparison.tax_comparison import start_comparison

menu_router = Router()

@menu_router.message(lambda message: message.text == "🧮 Калькуляторы")
async def handle_tax_calculator(message: Message):
    await message.answer(
        "📊 <b>Калькулятор налогов</b>\n\n"
        "Выберите систему налогообложения:",
        reply_markup=get_calculators_menu()
    )

# ИСПРАВЛЕННЫЙ ОБРАБОТЧИК - ДОБАВЛЯЕМ state
@menu_router.message(lambda message: message.text == "📊 Сравнить системы")
async def handle_tax_comparison(message: Message, state: FSMContext):
    await start_comparison(message, state)

@menu_router.message(lambda message: message.text == "💰 Вычеты")
async def handle_deductions(message: Message):
    await message.answer("🏠 <b>Налоговые вычеты</b>\n\nКакие вычеты вас интересуют?\n• Ипотечные\n• Лечение\n• Обучение\n• Инвестиционные")

@menu_router.message(lambda message: message.text == "📅 Отчетность")
async def handle_deadlines(message: Message):
    await message.answer("📅 <b>Сроки отчетности</b>\n\n• 3-НДФЛ: до 30 апреля\n• УСН: до 30 апреля (ИП)\n• Самозанятые: до 25 числа каждого месяца")

@menu_router.message(lambda message: message.text == "👤 Самозанятые")
async def handle_self_employed(message: Message):
    await message.answer("👤 <b>Помощь самозанятых</b>\n\n• Регистрация как самозанятый\n• Расчет налога 4-6%\n• Чекование доходов\n• Лимиты и ограничения")

@menu_router.message(lambda message: message.text == "⚙️ Настройки")
async def handle_reminders(message: Message):
    await message.answer("⚙️ <b>Настройки</b>\n\n• Уведомления о сроках\n• Язык интерфейса\n• Валюта расчетов")

@menu_router.message(lambda message: message.text == "🔙 Назад")
async def handle_back_to_main(message: Message):
    await message.answer("🎯 <b>Главное меню</b>")
    await message.answer(
        "Выберите раздел:",
        reply_markup=get_main_menu()
    )