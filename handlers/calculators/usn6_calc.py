# handlers/calculators/usn6_calc.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_main_menu
from keyboards.inline import get_callback_btns
from config import db

usn6_router = Router()

class USN6States(StatesGroup):
    waiting_for_income = State()

@usn6_router.message(F.text == "📊 УСН 6%")
async def start_usn6_calculator(message: Message, state: FSMContext):
    await message.answer(
        "📊 <b>Калькулятор УСН 6% (Доходы)</b>\n\n"
        "Введите ваш доход за квартал (в рублях):\n"
        "Пример: 300000"
    )
    await state.set_state(USN6States.waiting_for_income)

@usn6_router.message(USN6States.waiting_for_income)
async def calculate_usn6(message: Message, state: FSMContext):
    try:
        income = float(message.text)
        if income <= 0:
            await message.answer("❌ Доход должен быть положительным числом. Введите снова:")
            return
        
        # Расчет налога УСН 6%
        tax = income * 0.06
        net_income = income - tax
        
        # Сохраняем расчет в базу
        calculation = await db.save_calculation(
            user_id=message.from_user.id,
            calc_type="usn6",
            income=income,
            expenses=0,
            result_data={
                "tax": tax,
                "net_income": net_income,
                "calculation_type": "УСН 6%"
            }
        )
        
        # Основной результат
        await message.answer(
            f"📊 <b>Результат расчета УСН 6%:</b>\n\n"
            f"• Доход за квартал: {income:,.0f}₽\n"
            f"• Налог 6%: {tax:,.0f}₽\n"
            f"• Чистый доход: {net_income:,.0f}₽\n\n"
            f"<i>Налог уплачивается ежеквартально</i>"
        )
        
        # Монетизационное меню
        keyboard = get_callback_btns(
            btns={
                "🔄 Новый расчет": "new_usn6",
                "📊 Сравнить системы": "compare_after_calc",
                "💾 Сохранить (премиум)": "premium_save",
                "🏠 В главное меню": "main_menu"
            },
            sizes=(2, 1, 1)
        )

        await message.answer(
            "📊 <b>Расчет завершен!</b>\n\n"
            "💡 <i>Хотите больше возможностей?</i>\n"
            "• Сравнение всех налоговых систем\n"
            "• Сохранение истории расчетов\n"
            "• Персональные рекомендации\n\n"
            "🔓 <b>Премиум-функции разблокированы</b>",
            reply_markup=keyboard
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число. Пример: 300000")