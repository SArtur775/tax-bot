# handlers/calculators/ndfl_calc.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_main_menu
from keyboards.inline import get_callback_btns
from config import db  # Импортируем базу данных из config.py

ndfl_router = Router()

class NDFLStates(StatesGroup):
    waiting_for_income = State()

@ndfl_router.message(F.text == "💼 НДФЛ 13%")
async def start_ndfl_calculator(message: Message, state: FSMContext):
    # ПРОВЕРКА ЛИМИТА РАСЧЕТОВ
    can_calculate, used, remaining = await db.check_calculation_limit(message.from_user.id)
    is_premium = await db.check_premium_access(message.from_user.id)
    
    if not can_calculate:
        keyboard = get_callback_btns(
            btns={
                "💎 Купить премиум": "buy_premium",
                "🔙 Главное меню": "main_menu"
            },
            sizes=(2,)
        )
        
        await message.answer(
            f"🚫 <b>Лимит расчетов исчерпан!</b>\n\n"
            f"Вы использовали {used}/5 расчетов сегодня.\n\n"
            f"💎 <b>Премиум подписка</b> снимает все ограничения!\n"
            f"• Безлимитные расчеты\n"
            f"• Полная история\n"
            f"• Сравнение систем\n\n"
            f"Всего 299₽/месяц",
            reply_markup=keyboard
        )
        await state.clear()
        return
    
    # Показываем статус лимита
    if is_premium:
        limit_text = "💎 Премиум - безлимитные расчеты"
    else:
        limit_text = f"📊 Бесплатно: {remaining}/5 расчетов сегодня"
    
    await message.answer(
        f"📊 <b>Калькулятор НДФЛ 13%</b>\n\n"
        f"{limit_text}\n\n"
        "Введите ваш доход за месяц (в рублях):\n"
        "Пример: 100000"
    )
    await state.set_state(NDFLStates.waiting_for_income)

@ndfl_router.message(NDFLStates.waiting_for_income)
async def calculate_ndfl(message: Message, state: FSMContext):
    try:
        income = float(message.text)
        if income <= 0:
            await message.answer("❌ Доход должен быть положительным числом. Введите снова:")
            return
        
        # Расчет налога
        tax = income * 0.13
        net_income = income - tax
        
        # Сохраняем расчет в базу
        calculation = await db.save_calculation(
            user_id=message.from_user.id,
            calc_type="ndfl",
            income=income,
            expenses=0,
            result_data={
                "tax": tax,
                "net_income": net_income,
                "calculation_type": "НДФЛ 13%"
            }
        )
        
        # Основной результат
        await message.answer(
            f"📊 <b>Результат расчета НДФЛ:</b>\n\n"
            f"• Ваш доход: {income:,.0f}₽\n"
            f"• Налог 13%: {tax:,.0f}₽\n"
            f"• Чистый доход: {net_income:,.0f}₽\n\n"
            f"<i>Налог уплачивается работодателем</i>"
        )
        
        # Проверяем премиум для меню
        is_premium = await db.check_premium_access(message.from_user.id)
        
        if is_premium:
            # Меню для премиум пользователей
            keyboard = get_callback_btns(
                btns={
                    "🔄 Новый расчет": "new_ndfl",
                    "📊 Сравнить системы": "compare_after_calc",
                    "💾 Сохранить в историю": "save_to_history",
                    "🏠 В главное меню": "main_menu"
                },
                sizes=(2, 1, 1)
            )
            
            await message.answer(
                "✅ <b>Расчет сохранен в историю!</b>\n\n"
                "💎 Все премиум-функции доступны",
                reply_markup=keyboard
            )
        else:
            # Меню для бесплатных пользователей
            keyboard = get_callback_btns(
                btns={
                    "🔄 Новый расчет": "new_ndfl",
                    "📊 Сравнить системы": "premium_compare",
                    "💾 Сохранить (премиум)": "premium_save",
                    "💎 Купить премиум": "buy_premium",
                    "🏠 В главное меню": "main_menu"
                },
                sizes=(2, 1, 1, 1)
            )
            
            # Проверяем сколько расчетов осталось
            can_calculate, used, remaining = await db.check_calculation_limit(message.from_user.id)
            
            await message.answer(
                f"📊 <b>Расчет завершен!</b>\n\n"
                f"Осталось расчетов сегодня: {remaining}/5\n\n"
                "💡 <b>Хотите больше возможностей?</b>\n"
                "• Сравнение всех налоговых систем\n"
                "• Сохранение истории расчетов\n"
                "• Безлимитные расчеты\n\n"
                "💎 <b>Премиум подписка</b> всего за 299₽/месяц",
                reply_markup=keyboard
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число. Пример: 100000")

# Обработчики кнопок меню
@ndfl_router.callback_query(F.data == "new_ndfl")
async def new_ndfl_calculation(callback: CallbackQuery, state: FSMContext):
    await start_ndfl_calculator(callback.message, state)
    await callback.answer()

@ndfl_router.callback_query(F.data == "save_to_history")
async def save_to_history(callback: CallbackQuery):
    await callback.answer("✅ Расчет уже сохранен в вашу историю!", show_alert=True)

@ndfl_router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.answer("📍 Возвращаемся в главное меню:", reply_markup=get_main_menu())
    await callback.answer()