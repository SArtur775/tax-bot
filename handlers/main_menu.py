# handlers/main_menu.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_calculators_menu, get_main_menu
from keyboards.inline import get_callback_btns
from config import db

menu_router = Router()

@menu_router.message(F.text == "🧮 Калькуляторы")
async def handle_tax_calculator(message: Message):
    user_id = message.from_user.id
    can_calculate, used, remaining = await db.check_calculation_limit(user_id)
    is_premium = await db.check_premium_access(user_id)
    
    if is_premium:
        status_text = "💎 Премиум - безлимитные расчеты"
    else:
        status_text = f"📊 Бесплатно: {remaining}/5 расчетов сегодня"
    
    await message.answer(
        f"🧮 <b>Налоговые калькуляторы</b>\n\n"
        f"{status_text}\n\n"
        f"Выберите систему налогообложения:",
        reply_markup=get_calculators_menu()
    )

@menu_router.message(F.text == "📊 Сравнить системы")
async def handle_tax_comparison(message: Message, state: FSMContext):
    user_id = message.from_user.id
    is_premium = await db.check_premium_access(user_id)
    
    if not is_premium:
        keyboard = get_callback_btns(
            btns={
                "💎 Купить премиум": "buy_premium",
                "🔙 Главное меню": "main_menu"
            },
            sizes=(2,)
        )
        
        await message.answer(
            "🔒 <b>Сравнение систем доступно в премиум версии</b>\n\n"
            "💎 <b>Премиум подписка</b> всего за 299₽/месяц:\n"
            "• Сравнение всех налоговых систем\n"
            "• Безлимитные расчеты\n"
            "• Полная история расчетов\n"
            "• Приоритетная поддержка\n\n"
            "Откройте все возможности бота! 🚀",
            reply_markup=keyboard
        )
        return
    
    # Если премиум есть, запускаем сравнение
    from handlers.comparison.tax_comparison import start_comparison
    await start_comparison(message, state)

@menu_router.message(F.text == "💰 Вычеты")
async def handle_deductions(message: Message):
    keyboard = get_callback_btns(
        btns={
            "🏠 Ипотечные": "mortgage_deduction",
            "🏥 Лечение": "treatment_deduction",
            "🎓 Обучение": "education_deduction", 
            "📈 Инвестиционные": "investment_deduction",
            "🔙 Назад": "main_menu"
        },
        sizes=(2, 2, 1)
    )
    
    await message.answer(
        "🏠 <b>Налоговые вычеты</b>\n\n"
        "Вы можете вернуть до 13% от расходов:\n\n"
        "• 🏠 Ипотечные - до 260 тыс.₽/год\n"
        "• 🏥 Лечение - до 50 тыс.₽/год\n"
        "• 🎓 Обучение - до 50 тыс.₽/год\n"
        "• 📈 Инвестиционные - до 52 тыс.₽/год\n\n"
        "Выберите тип вычета:",
        reply_markup=keyboard
    )

@menu_router.message(F.text == "📅 Отчетность")
async def handle_deadlines(message: Message):
    await message.answer(
        "📅 <b>Сроки отчетности и уплаты налогов</b>\n\n"
        "<b>📊 3-НДФЛ:</b>\n"
        "• Декларация: до 30 апреля\n"
        "• Уплата налога: до 15 июля\n\n"
        "<b>💼 УСН:</b>\n"
        "• Авансовые платежи: до 25 числа месяца после квартала\n"
        "• Декларация: до 30 апреля (ИП), до 31 марта (ООО)\n\n"
        "<b>👤 Самозанятые:</b>\n"
        "• Уплата налога: до 25 числа каждого месяца\n\n"
        "<b>🏢 НДС:</b>\n"
        "• Декларация: до 25 числа месяца после квартала"
    )

@menu_router.message(F.text == "👤 Самозанятые")
async def handle_self_employed(message: Message):
    keyboard = get_callback_btns(
        btns={
            "📝 Регистрация": "self_employed_registration",
            "🧮 Калькулятор": "self_employed_calc",
            "🧾 Чекование": "self_employed_receipts",
            "📊 Лимиты": "self_employed_limits",
            "🔙 Назад": "main_menu"
        },
        sizes=(2, 2, 1)
    )
    
    await message.answer(
        "👤 <b>Помощь самозанятым</b>\n\n"
        "Все для работы на специальном налоговом режиме:\n\n"
        "• 📝 Регистрация как самозанятый\n"
        "• 🧮 Расчет налога 4-6%\n"
        "• 🧾 Чекование доходов\n"
        "• 📊 Лимиты и ограничения\n"
        "• 💼 Переход на ИП\n\n"
        "Выберите раздел:",
        reply_markup=keyboard
    )

@menu_router.message(F.text == "📈 Моя статистика")
async def show_my_stats(message: Message):
    user_id = message.from_user.id
    stats = await db.get_user_stats(user_id)
    is_premium = await db.check_premium_access(user_id)
    
    if is_premium:
        premium_status = "💎 Премиум аккаунт"
        if stats['subscription']:
            subscription_info = f"\n📅 Подписка действует до: {stats['subscription']['expires_at']}"
        else:
            subscription_info = ""
    else:
        premium_status = "🔓 Бесплатный аккаунт"
        subscription_info = "\n💡 Используйте /premium для расширения возможностей"
    
    calc_types_text = "\n".join([f"• {calc_type}: {count}" for calc_type, count in stats['calc_types'].items()])
    
    await message.answer(
        f"📈 <b>Ваша статистика</b>\n\n"
        f"{premium_status}{subscription_info}\n"
        f"📊 Всего расчетов: {stats['total_calculations']}\n\n"
        f"<b>По типам:</b>\n{calc_types_text}\n\n"
        f"💎 Премиум открывает:\n"
        f"• Безлимитные расчеты\n"
        f"• Сравнение систем\n"
        f"• Полную историю",
        reply_markup=get_main_menu()
    )

@menu_router.message(F.text == "⚙️ Настройки")
async def handle_settings(message: Message):
    keyboard = get_callback_btns(
        btns={
            "🔔 Уведомления": "settings_notifications",
            "🌐 Язык": "settings_language", 
            "💰 Валюта": "settings_currency",
            "📊 Статистика": "my_stats",
            "🔙 Назад": "main_menu"
        },
        sizes=(2, 2, 1)
    )
    
    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Настройте бота под себя:\n\n"
        "• 🔔 Уведомления о сроках отчетности\n"
        "• 🌐 Язык интерфейса\n"
        "• 💰 Валюта расчетов (₽/$/€)\n"
        "• 📊 Персональная статистика\n\n"
        "Выберите настройку:",
        reply_markup=keyboard
    )

@menu_router.message(F.text == "🔙 Назад")
async def handle_back_to_main(message: Message):
    await message.answer(
        "🎯 <b>Главное меню</b>\n\n"
        "Выберите раздел:",
        reply_markup=get_main_menu()
    )

# Обработчики для кнопок меню
@menu_router.callback_query(F.data == "my_stats")
async def show_stats_from_callback(callback: CallbackQuery):
    await show_my_stats(callback.message)
    await callback.answer()

@menu_router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.answer(
        "🎯 <b>Главное меню</b>\n\n"
        "Выберите раздел:",
        reply_markup=get_main_menu()
    )
    await callback.answer()