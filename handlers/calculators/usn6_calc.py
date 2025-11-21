# handlers/calculators/usn6_calc.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

usn6_router = Router()

class USN6States(StatesGroup):
    waiting_for_income = State()

@usn6_router.message(F.text == "УСН 6%")
async def start_usn6_calculator(message: Message, state: FSMContext):
    await message.answer(
        "📊 <b>Калькулятор УСН 6% (Доходы)</b>\n\n"
        "Введите ваш доход за квартал (в рублях):\n"
        "Пример: 300000",
        parse_mode="HTML"
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
        
        await message.answer(
            f"📊 <b>Результат расчета УСН 6%:</b>\n\n"
            f"• Доход за квартал: {income:,.0f}₽\n"
            f"• Налог 6%: {tax:,.0f}₽\n"
            f"• Чистый доход: {net_income:,.0f}₽\n\n"
            f"<i>Налог уплачивается ежеквартально</i>",
            parse_mode="HTML"
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число. Пример: 300000")