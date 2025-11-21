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
    
    # Проверяем лимиты и премиум статус
    can_calculate, used, remaining = await db.check_calculation_limit(message.from_user.id)
    is_premium = await db.check_premium_access(message.from_user.id)
    
    if is_premium:
        limit_text = "💎 Премиум - безлимитные расчеты"
    else:
        limit_text = f"📊 Бесплатно: {remaining}/5 расчетов сегодня"
    
    # Первое сообщение - приветствие с лимитами
    await message.answer(
        f"👋 <b>Добро пожаловать в Налоговый Помощник!</b>\n\n"
        f"{limit_text}\n\n"
        f"Я помогу вам:\n"
        f"• 📊 Рассчитать налоги\n"
        f"• 🔍 Сравнить системы\n"
        f"• 💰 Оптимизировать платежи\n"
        f"• 🏠 Получить вычеты\n\n"
        f"💎 <b>Премиум подписка</b> открывает все возможности!"
    )
    
    # Второе сообщение - кнопки
    await message.answer(
        "🎯 <b>Выберите раздел:</b>",
        reply_markup=get_main_menu()
    )

@start_router.message(Command("menu"))
async def cmd_menu(message: Message):
    # Проверяем лимиты для отображения в меню
    user_id = message.from_user.id
    can_calculate, used, remaining = await db.check_calculation_limit(user_id)
    is_premium = await db.check_premium_access(user_id)
    
    if is_premium:
        status_text = "💎 Премиум - все функции доступны"
    else:
        status_text = f"📊 Бесплатно: {remaining}/5 расчетов сегодня"
    
    await message.answer(
        f"🎯 <b>Главное меню</b>\n\n"
        f"{status_text}"
    )
    await message.answer(
        "Выберите раздел:",
        reply_markup=get_main_menu()
    )

@start_router.message(Command("help"))
async def cmd_help(message: Message):
    user_id = message.from_user.id
    is_premium = await db.check_premium_access(user_id)
    
    if is_premium:
        premium_features = "✅ Все премиум функции активны"
    else:
        premium_features = (
            "💎 <b>Премиум функции:</b>\n"
            "• Безлимитные расчеты\n"
            "• Сравнение налоговых систем\n"
            "• Полная история расчетов\n"
            "• Используйте /premium для подключения"
        )
    
    await message.answer(
        f"🆘 <b>Помощь по боту</b>\n\n"
        f"<b>Основные команды:</b>\n"
        f"/start - Главное меню\n"
        f"/menu - Быстрое меню\n"
        f"/premium - Информация о подписке\n"
        f"/mysubscription - Статус подписки\n"
        f"/history - История расчетов\n"
        f"/help - Эта справка\n\n"
        f"<b>Калькуляторы:</b>\n"
        f"• НДФЛ 13% - для наемных работников\n"
        f"• УСН 6% - упрощенка 'доходы'\n"
        f"• УСН 15% - упрощенка 'доходы-расходы'\n"
        f"• Самозанятый - специальный режим\n\n"
        f"{premium_features}\n\n"
        f"💡 <b>Совет:</b> Начните с калькуляторов или сравнения систем!"
    )