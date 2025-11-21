# handlers/calculators/ndfl_calc.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

ndfl_router = Router()

class NDFLStates(StatesGroup):
    waiting_for_income = State()

@ndfl_router.message(F.text == "НДФЛ 13%")
async def start_ndfl_calculator(message: Message, state: FSMContext):
    await message.answer(
        "📊 <b>Калькулятор НДФЛ 13%</b>\n\n"
        "Введите ваш доход за месяц (в рублях):\n"
        "Пример: 100000",
        parse_mode="HTML"
    )
    await state.set_state(NDFLStates.waiting_for_income)

@ndfl_router.message(NDFLStates.waiting_for_income)
async def calculate_ndfl(message: Message, state: FSMContext):
    try:
        income = float(message.text)
        if income <= 0:
            await message.answer("❌ Доход должен быть положительным числом. Введите снова:")
            return
        
        tax = income * 0.13
        net_income = income - tax
        
        await message.answer(
            f"📊 <b>Результат расчета НДФЛ:</b>\n\n"
            f"• Ваш доход: {income:,.0f}₽\n"
            f"• Налог 13%: {tax:,.0f}₽\n"
            f"• Чистый доход: {net_income:,.0f}₽\n\n"
            f"<i>Налог уплачивается работодателем</i>",
            parse_mode="HTML"
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число. Пример: 100000")