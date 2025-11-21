# handlers/premium/premium_handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.reply import get_main_menu, get_calculators_menu
from keyboards.inline import get_callback_btns

premium_router = Router()

@premium_router.callback_query(F.data.startswith("premium_"))
async def offer_premium(callback: CallbackQuery):
    feature = callback.data.replace("premium_", "")
    
    premium_features = {
        "compare": "📊 Сравнение налоговых систем",
        "save": "💾 Сохранение истории расчетов", 
    }
    
    # Клавиатура с кнопкой "Назад"
    keyboard = get_callback_btns(
        btns={"🔙 Назад к меню": "main_menu"},
        sizes=(1,)
    )
    
    await callback.message.answer(
        f"🚀 <b>{premium_features[feature]}</b>\n\n"
        "Эта функция доступна в премиум-версии:\n\n"
        "💎 <b>Премиум подписка</b>\n"
        "• Все калькуляторы без ограничений\n"
        "• Сравнение налоговых систем\n"  
        "• Сохранение истории расчетов\n"
        "• Персональные рекомендации\n"
        "• Приоритетная поддержка\n\n"
        "💰 <b>Всего 299₽/месяц</b>\n\n"
        "👉 Напишите 'премиум' для подключения",
        reply_markup=keyboard
    )
    await callback.answer()

# Обработчик для сравнения после расчета
@premium_router.callback_query(F.data == "compare_after_calc")
async def start_comparison_after_calc(callback: CallbackQuery):
    from keyboards.inline import get_callback_btns
    
    keyboard = get_callback_btns(
        btns={
            "💼 Наемный работник": "employee",
            "👨‍💼 Фрилансер/ИП": "freelancer", 
            "🏢 Бизнес с расходами": "business",
            "👤 Самозанятый": "self_employed"
        },
        sizes=(2, 2)
    )
    
    await callback.message.answer(
        "🔍 <b>Сравнение налоговых систем</b>\n\n"
        "Выберите ваш тип деятельности:",
        reply_markup=keyboard
    )
    await callback.answer()

@premium_router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.answer("📍 Возвращаемся в главное меню:", reply_markup=get_main_menu())
    await callback.answer()

@premium_router.callback_query(F.data.startswith("new_"))
async def new_calculation(callback: CallbackQuery):
    calc_type = callback.data.replace("new_", "")
    
    calculators = {
        "ndfl": "НДФЛ 13%",
        "usn6": "УСН 6%", 
        "usn15": "УСН 15%",
        "self_employed": "Самозанятый 4-6%"
    }
    
    if calc_type in calculators:
        await callback.message.answer(
            f"🔄 Начинаем новый расчет: {calculators[calc_type]}\n"
            f"Введите данные для расчета...",
            reply_markup=get_calculators_menu()
        )
    await callback.answer()

# Добавляем обработчик текстового сообщения "премиум"
@premium_router.message(F.text.lower() == "премиум")
async def handle_premium_text(message: Message):
    keyboard = get_callback_btns(
        btns={"🔙 Назад к меню": "main_menu"},
        sizes=(1,)
    )
    
    await message.answer(
        "💎 <b>Премиум подписка</b>\n\n"
        "Что вы получите:\n"
        "• 📊 Сравнение всех налоговых систем\n"
        "• 💾 Сохранение истории расчетов\n"  
        "• 🔍 Персональные рекомендации\n"
        "• ⚡ Приоритетная поддержка\n"
        "• 📈 Расширенная аналитика\n\n"
        "💰 <b>299₽/месяц</b>\n\n"
        "Для подключения напишите нам: @YourSupportUsername",
        reply_markup=keyboard
    )