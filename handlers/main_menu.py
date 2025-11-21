# handlers/main_menu.py
from aiogram import Router
from aiogram.types import Message
from keyboards.calculators_menu import get_calculators_menu
from keyboards.main_menu import get_main_menu  # Добавляем импорт

menu_router = Router()

@menu_router.message(lambda message: message.text == "🔄 Калькулятор налогов")
async def handle_tax_calculator(message: Message):
    await message.answer(
        "📊 <b>Калькулятор налогов</b>\n\n"
        "Выберите систему налогообложения:",
        reply_markup=get_calculators_menu(),
        parse_mode="HTML"
    )

@menu_router.message(lambda message: message.text == "💰 Налоговые вычеты")
async def handle_deductions(message: Message):
    await message.answer("🏠 <b>Налоговые вычеты</b>\n\nКакие вычеты вас интересуют?\n• Ипотечные\n• Лечение\n• Обучение\n• Инвестиционные", parse_mode="HTML")

@menu_router.message(lambda message: message.text == "📅 Сроки отчетности")
async def handle_deadlines(message: Message):
    await message.answer("📅 <b>Сроки отчетности</b>\n\n• 3-НДФЛ: до 30 апреля\n• УСН: до 30 апреля (ИП)\n• Самозанятые: до 25 числа каждого месяца", parse_mode="HTML")

@menu_router.message(lambda message: message.text == "👤 Помощь самозанятым")
async def handle_self_employed(message: Message):
    await message.answer("👤 <b>Помощь самозанятых</b>\n\n• Регистрация как самозанятый\n• Расчет налога 4-6%\n• Чекование доходов\n• Лимиты и ограничения", parse_mode="HTML")

@menu_router.message(lambda message: message.text == "🔔 Напоминания")
async def handle_reminders(message: Message):
    await message.answer("🔔 <b>Напоминания</b>\n\nНастройте уведомления о:\n• Сроках сдачи отчетности\n• Уплате налогов\n• Изменениях в законодательстве", parse_mode="HTML")

# ДОБАВЛЯЕМ ОБРАБОТЧИК КНОПКИ "НАЗАД"
@menu_router.message(lambda message: message.text == "🔙 Назад в главное меню")
async def handle_back_to_main(message: Message):
    await message.answer(
        "📍 Возвращаемся в главное меню:",
        reply_markup=get_main_menu()
    )