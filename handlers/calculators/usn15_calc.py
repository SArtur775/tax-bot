# handlers/calculators/usn15_calc.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

usn15_router = Router()

class USN15States(StatesGroup):
    waiting_for_data = State()

@usn15_router.message(F.text == "УСН 15%")
async def start_usn15_calculator(message: Message, state: FSMContext):
    await message.answer(
        "📊 <b>Калькулятор УСН 15% (Доходы-Расходы)</b>\n\n"
        "Введите ваш доход за квартал (в рублях):\n"
        "Пример: 500000",
        parse_mode="HTML"
    )
    await state.set_state(USN15States.waiting_for_data)
    await state.update_data(step="income")

@usn15_router.message(USN15States.waiting_for_data)
async def calculate_usn15(message: Message, state: FSMContext):
    user_data = await state.get_data()
    
    try:
        if user_data.get("step") == "income":
            income = float(message.text)
            await state.update_data(income=income)
            await message.answer(
                "Теперь введите ваши расходы за квартал (в рублях):\n"
                "Пример: 200000"
            )
            await state.update_data(step="expenses")
        else:
            expenses = float(message.text)
            income = user_data["income"]
            
            if expenses >= income:
                await message.answer("❌ Расходы не могут быть больше или равны доходам. Введите снова:")
                return
            
            # Расчет налога УСН 15%
            tax_base = income - expenses
            tax = tax_base * 0.15
            net_income = income - expenses - tax
            
            await message.answer(
                f"📊 <b>Результат расчета УСН 15%:</b>\n\n"
                f"• Доход за квартал: {income:,.0f}₽\n"
                f"• Расходы за квартал: {expenses:,.0f}₽\n"
                f"• Налоговая база: {tax_base:,.0f}₽\n"
                f"• Налог 15%: {tax:,.0f}₽\n"
                f"• Чистый доход: {net_income:,.0f}₽\n\n"
                f"<i>Минимальный налог 1% от дохода: {income * 0.01:,.0f}₽</i>",
                parse_mode="HTML"
            )
            await state.clear()
            
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число.")