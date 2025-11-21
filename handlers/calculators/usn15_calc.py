# handlers/calculators/usn15_calc.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_main_menu
from keyboards.inline import get_callback_btns
from config import db

usn15_router = Router()

class USN15States(StatesGroup):
    waiting_for_income = State()
    waiting_for_expenses = State()

@usn15_router.message(F.text == "📈 УСН 15%")
async def start_usn15_calculator(message: Message, state: FSMContext):
    await message.answer(
        "📊 <b>Калькулятор УСН 15% (Доходы-Расходы)</b>\n\n"
        "Введите ваш доход за квартал (в рублях):\n"
        "Пример: 500000"
    )
    await state.set_state(USN15States.waiting_for_income)

@usn15_router.message(USN15States.waiting_for_income)
async def process_income(message: Message, state: FSMContext):
    try:
        income = float(message.text)
        if income <= 0:
            await message.answer("❌ Доход должен быть положительным числом. Введите снова:")
            return
        
        await state.update_data(income=income)
        await message.answer(
            f"✅ Доход: {income:,.0f}₽\n\n"
            "Теперь введите ваши расходы за квартал (в рублях):\n"
            "Пример: 200000"
        )
        await state.set_state(USN15States.waiting_for_expenses)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число. Пример: 500000")

@usn15_router.message(USN15States.waiting_for_expenses)
async def calculate_usn15(message: Message, state: FSMContext):
    try:
        expenses = float(message.text)
        user_data = await state.get_data()
        income = user_data['income']
        
        if expenses < 0:
            await message.answer("❌ Расходы не могут быть отрицательными. Введите снова:")
            return
            
        if expenses >= income:
            await message.answer("❌ Расходы не могут быть больше или равны доходам. Введите снова:")
            return
        
        # Расчет налога УСН 15%
        tax_base = income - expenses
        tax = tax_base * 0.15
        net_income = income - expenses - tax
        
        # Минимальный налог (1% от доходов)
        min_tax = income * 0.01
        
        tax_info = ""
        if tax < min_tax:
            tax_info = f"• <b>Минимальный налог 1%:</b> {min_tax:,.0f}₽ (применяется, так как он больше рассчитанного)\n"
            actual_tax = min_tax
            actual_net_income = income - expenses - min_tax
        else:
            tax_info = f"• <b>Налог 15%:</b> {tax:,.0f}₽\n"
            actual_tax = tax
            actual_net_income = net_income
        
        # Сохраняем расчет в базу
        calculation = await db.save_calculation(
            user_id=message.from_user.id,
            calc_type="usn15",
            income=income,
            expenses=expenses,
            result_data={
                "tax_base": tax_base,
                "tax": actual_tax,
                "net_income": actual_net_income,
                "min_tax": min_tax,
                "calculation_type": "УСН 15%",
                "tax_info": "минимальный налог" if tax < min_tax else "обычный налог"
            }
        )
        
        # Основной результат
        await message.answer(
            f"📊 <b>Результат расчета УСН 15%:</b>\n\n"
            f"• Доход за квартал: {income:,.0f}₽\n"
            f"• Расходы за квартал: {expenses:,.0f}₽\n"
            f"• Налоговая база: {tax_base:,.0f}₽\n"
            f"{tax_info}"
            f"• <b>Итоговый налог к уплате:</b> {actual_tax:,.0f}₽\n"
            f"• <b>Чистый доход:</b> {actual_net_income:,.0f}₽\n\n"
            f"<i>Налог уплачивается ежеквартально</i>"
        )
        
        # Монетизационное меню
        keyboard = get_callback_btns(
            btns={
                "🔄 Новый расчет": "new_usn15",
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
        await message.answer("❌ Пожалуйста, введите число. Пример: 200000")