# handlers/premium/premium_handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from keyboards.reply import get_main_menu, get_calculators_menu
from keyboards.inline import get_callback_btns
from config import db

premium_router = Router()

# Команда /premium - информация о тарифах
@premium_router.message(Command("premium"))
@premium_router.message(F.text.lower() == "премиум")
async def show_premium_info(message: Message):
    user_id = message.from_user.id
    is_premium = await db.check_premium_access(user_id)
    
    if is_premium:
        subscription = await db.get_user_subscription(user_id)
        if subscription:
            expires_date = subscription.expires_at.strftime("%d.%m.%Y")
            await message.answer(
                f"💎 <b>У вас активна премиум подписка!</b>\n\n"
                f"✅ Доступ открыт до: {expires_date}\n"
                f"📋 Тариф: {subscription.plan}\n\n"
                f"Все функции разблокированы! 🚀",
                reply_markup=get_main_menu()
            )
        return
    
    keyboard = get_callback_btns(
        btns={
            "💰 Купить премиум (299₽/мес)": "buy_premium",
            "📊 Посмотреть тарифы": "show_plans", 
            "🔙 Назад": "main_menu"
        },
        sizes=(2, 1)
    )
    
    await message.answer(
        "💎 <b>Премиум подписка</b>\n\n"
        "Что вы получите:\n"
        "• ✅ Все калькуляторы без ограничений\n"
        "• 📊 Сравнение налоговых систем\n"
        "• 💾 Полная история расчетов\n"  
        "• 🔍 Персональные рекомендации\n"
        "• ⚡ Приоритетная поддержка\n"
        "• 📈 Расширенная аналитика\n\n"
        "💰 <b>299₽/месяц</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )

# Команда /mysubscription - статус подписки
@premium_router.message(Command("mysubscription"))
async def show_my_subscription(message: Message):
    user_id = message.from_user.id
    is_premium = await db.check_premium_access(user_id)
    
    if is_premium:
        subscription = await db.get_user_subscription(user_id)
        if subscription:
            expires_date = subscription.expires_at.strftime("%d.%m.%Y")
            await message.answer(
                f"💎 <b>Ваша подписка</b>\n\n"
                f"✅ Статус: Активна\n"
                f"📋 Тариф: {subscription.plan}\n"
                f"📅 Истекает: {expires_date}\n"
                f"🔢 ID: {subscription.id}",
                reply_markup=get_main_menu()
            )
    else:
        await message.answer(
            "🔒 <b>У вас нет активной подписки</b>\n\n"
            "Для доступа ко всем функциям оформите премиум подписку:\n"
            "Напишите <b>/premium</b>",
            reply_markup=get_main_menu()
        )

# Покупка премиума
@premium_router.callback_query(F.data == "buy_premium")
async def buy_premium(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_premium = await db.check_premium_access(user_id)
    
    if is_premium:
        await callback.message.answer("✅ У вас уже есть премиум подписка!")
        await callback.answer()
        return
    
    # Здесь будет интеграция с платежной системой
    # Пока заглушка
    keyboard = get_callback_btns(
        btns={
            "💳 Оплатить 299₽": "process_payment",
            "🔙 Назад": "premium_info"
        },
        sizes=(2,)
    )
    
    await callback.message.answer(
        "💳 <b>Оплата премиум подписки</b>\n\n"
        "Сумма: 299₽\n"
        "Период: 1 месяц\n\n"
        "После оплата вы получите:\n"
        "• Полный доступ ко всем функциям\n"
        "• Приоритетную поддержку\n"
        "• Историю расчетов\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )
    await callback.answer()

# Заглушка для обработки платежа
@premium_router.callback_query(F.data == "process_payment")
async def process_payment(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Заглушка - имитация успешной оплаты
    try:
        subscription = await db.create_subscription(
            user_id=user_id,
            plan='premium',
            months=1,
            payment_id=f"test_{user_id}_{datetime.utcnow().timestamp()}"
        )
        
        await callback.message.answer(
            "🎉 <b>Поздравляем!</b>\n\n"
            "✅ Премиум подписка активирована!\n"
            "📅 Действует до: " + subscription.expires_at.strftime("%d.%m.%Y") + "\n\n"
            "Теперь вам доступны все функции бота! 🚀",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        await callback.message.answer(
            "❌ <b>Ошибка при активации подписки</b>\n\n"
            "Пожалуйста, попробуйте позже или обратитесь в поддержку.",
            reply_markup=get_main_menu()
        )
    
    await callback.answer()

# Показ тарифов
@premium_router.callback_query(F.data == "show_plans")
async def show_plans(callback: CallbackQuery):
    keyboard = get_callback_btns(
        btns={
            "💎 Premium - 299₽/мес": "buy_premium",
            "🚀 Pro - 599₽/мес": "buy_pro", 
            "🔙 Назад": "premium_info"
        },
        sizes=(2, 1)
    )
    
    await callback.message.answer(
        "📋 <b>Тарифные планы</b>\n\n"
        
        "💎 <b>Premium (299₽/месяц)</b>\n"
        "• Все калькуляторы без ограничений\n"
        "• Сравнение налоговых систем\n"
        "• Полная история расчетов\n"
        "• Приоритетная поддержка\n\n"
        
        "🚀 <b>Pro (599₽/месяц)</b>\n"
        "• Всё из Premium +\n"
        "• ИИ-консультации\n"
        "• Экспорт отчетов\n"
        "• Персональный анализ\n\n"
        
        "Выберите тариф:",
        reply_markup=keyboard
    )
    await callback.answer()

# Обработка премиум функций из меню калькуляторов
@premium_router.callback_query(F.data == "premium_compare")
async def handle_premium_compare(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки сравнения из меню калькуляторов"""
    user_id = callback.from_user.id
    is_premium = await db.check_premium_access(user_id)
    
    if not is_premium:
        keyboard = get_callback_btns(
            btns={
                "💎 Купить премиум": "buy_premium",
                "🔙 Главное меню": "main_menu"
            },
            sizes=(2,)
        )
        
        await callback.message.answer(
            "🔒 <b>Сравнение систем доступно в премиум версии</b>\n\n"
            "💎 <b>Премиум подписка</b> всего за 299₽/месяц:\n"
            "• Сравнение всех налоговых систем\n"
            "• Безлимитные расчеты\n"
            "• Полная история расчетов\n"
            "• Приоритетная поддержка\n\n"
            "Откройте все возможности бота! 🚀",
            reply_markup=keyboard
        )
    else:
        # Если премиум есть, запускаем сравнение с кнопкой назад
        keyboard = get_callback_btns(
            btns={
                "💼 Наемный работник": "employee",
                "👨‍💼 Фрилансер/ИП": "freelancer", 
                "🏢 Бизнес с расходами": "business",
                "👤 Самозанятый": "self_employed",
                "🔙 Назад": "main_menu"
            },
            sizes=(2, 2, 1)
        )
        
        await callback.message.answer(
            "🔍 <b>Сравнение налоговых систем</b>\n\n"
            "Выберите ваш тип деятельности:",
            reply_markup=keyboard
        )
    
    await callback.answer()

@premium_router.callback_query(F.data == "premium_save")
async def handle_premium_save(callback: CallbackQuery):
    """Обработчик кнопки сохранения из меню калькуляторов"""
    user_id = callback.from_user.id
    is_premium = await db.check_premium_access(user_id)
    
    if not is_premium:
        keyboard = get_callback_btns(
            btns={
                "💎 Купить премиум": "buy_premium", 
                "🔙 Главное меню": "main_menu"
            },
            sizes=(2,)
        )
        
        await callback.message.answer(
            "🔒 <b>Сохранение истории доступно в премиум версии</b>\n\n"
            "💎 <b>Премиум подписка</b> всего за 299₽/месяц:\n"
            "• Полная история всех расчетов\n"
            "• Безлимитные расчеты\n" 
            "• Сравнение налоговых систем\n"
            "• Приоритетная поддержка\n\n"
            "Сохраняйте все ваши расчеты! 💾",
            reply_markup=keyboard
        )
    else:
        await callback.answer("✅ Все расчеты автоматически сохраняются в историю!", show_alert=True)
    
    await callback.answer()

# Обработка премиум функций (старая версия для совместимости)
@premium_router.callback_query(F.data.startswith("premium_"))
async def handle_premium_feature(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_premium = await db.check_premium_access(user_id)
    
    if not is_premium:
        feature = callback.data.replace("premium_", "")
        
        premium_features = {
            "compare": "📊 Сравнение налоговых систем",
            "save": "💾 Сохранение истории расчетов", 
        }
        
        keyboard = get_callback_btns(
            btns={
                "💎 Купить премиум": "buy_premium",
                "🔙 Главное меню": "main_menu"
            },
            sizes=(2,)
        )
        
        await callback.message.answer(
            f"🚀 <b>{premium_features[feature]}</b>\n\n"
            "Эта функция доступна только в премиум-версии!\n\n"
            "💎 <b>Премиум подписка</b> всего за 299₽/месяц\n"
            "Откройте все возможности бота!",
            reply_markup=keyboard
        )
    else:
        # Если премиум есть, перенаправляем на соответствующую функцию
        feature = callback.data.replace("premium_", "")
        if feature == "compare":
            keyboard = get_callback_btns(
                btns={
                    "💼 Наемный работник": "employee",
                    "👨‍💼 Фрилансер/ИП": "freelancer", 
                    "🏢 Бизнес с расходами": "business",
                    "👤 Самозанятый": "self_employed",
                    "🔙 Главное меню": "main_menu"
                },
                sizes=(2, 2, 1)
            )
            
            await callback.message.answer(
                "🔍 <b>Сравнение налоговых систем</b>\n\n"
                "Выберите ваш тип деятельности:",
                reply_markup=keyboard
            )
    
    await callback.answer()

# Навигация
@premium_router.callback_query(F.data == "premium_info")
async def back_to_premium_info(callback: CallbackQuery):
    await show_premium_info(callback.message)
    await callback.answer()

@premium_router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.answer("📍 Возвращаемся в главное меню:", reply_markup=get_main_menu())
    await callback.answer()

# Сравнение систем (для премиум пользователей)
async def start_comparison_after_calc(callback: CallbackQuery):
    keyboard = get_callback_btns(
        btns={
            "💼 Наемный работник": "employee",
            "👨‍💼 Фрилансер/ИП": "freelancer", 
            "🏢 Бизнес с расходами": "business",
            "👤 Самозанятый": "self_employed",
            "🔙 Главное меню": "main_menu"
        },
        sizes=(2, 2, 1)
    )
    
    await callback.message.answer(
        "🔍 <b>Сравнение налоговых систем</b>\n\n"
        "Выберите ваш тип деятельности:",
        reply_markup=keyboard
    )
    await callback.answer()

@premium_router.callback_query(F.data == "buy_pro")
async def buy_pro_plan(callback: CallbackQuery):
    keyboard = get_callback_btns(
        btns={
            "💎 Оформить Premium": "buy_premium",
            "🔙 Назад": "premium_info"
        },
        sizes=(2,)
    )
    
    await callback.message.answer(
        "🚀 <b>Тариф Pro</b>\n\n"
        "В разработке... Скоро будет доступен!\n"
        "А пока можете оформить Premium подписку 💎",
        reply_markup=keyboard
    )
    await callback.answer()

# Обработчики для кнопок из калькуляторов
@premium_router.callback_query(F.data == "compare_after_calc")
async def handle_compare_after_calc(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки сравнения после расчета"""
    user_id = callback.from_user.id
    is_premium = await db.check_premium_access(user_id)
    
    if not is_premium:
        keyboard = get_callback_btns(
            btns={
                "💎 Купить премиум": "buy_premium",
                "🔙 Главное меню": "main_menu"
            },
            sizes=(2,)
        )
        
        await callback.message.answer(
            "🔒 <b>Сравнение систем доступно в премиум версии</b>\n\n"
            "💎 <b>Премиум подписка</b> всего за 299₽/месяц:\n"
            "• Сравнение всех налоговых систем\n"
            "• Безлимитные расчеты\n"
            "• Полная история расчетов\n"
            "• Приоритетная поддержка\n\n"
            "Откройте все возможности бота! 🚀",
            reply_markup=keyboard
        )
    else:
        # Если премиум есть, запускаем сравнение с кнопкой назад
        keyboard = get_callback_btns(
            btns={
                "💼 Наемный работник": "employee",
                "👨‍💼 Фрилансер/ИП": "freelancer", 
                "🏢 Бизнес с расходами": "business",
                "👤 Самозанятый": "self_employed",
                "🔙 Главное меню": "main_menu"
            },
            sizes=(2, 2, 1)
        )
        
        await callback.message.answer(
            "🔍 <b>Сравнение налоговых систем</b>\n\n"
            "Выберите ваш тип деятельности:",
            reply_markup=keyboard
        )
    
    await callback.answer()