# handlers/calculators/self_employed_calc.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_main_menu
from keyboards.inline import get_callback_btns
from config import db

self_employed_router = Router()

class SelfEmployedStates(StatesGroup):
    waiting_for_income_amount = State()

@self_employed_router.message(F.text == "👤 Самозанятый")
async def start_self_employed_calculator(message: Message):
    keyboard = get_callback_btns(
        btns={
            "💁 Физлица (4%)": "self_employed_4",
            "🏢 ИП/Компании (6%)": "self_employed_6", 
            "🔄 Смешанно (5%)": "self_employed_mixed"
        },
        sizes=(2, 1)
    )
    
    await message.answer(
        "👤 <b>Калькулятор для самозанятых</b>\n\n"
        "Выберите тип клиентов:",
        reply_markup=keyboard
    )

@self_employed_router.callback_query(F.data.startswith("self_employed_"))
async def process_client_type(callback: CallbackQuery, state: FSMContext):
    tax_rates = {
        "self_employed_4": (0.04, "физлицами"),
        "self_employed_6": (0.06, "ИП/компаниями"), 
        "self_employed_mixed": (0.05, "смешанно")
    }
    
    tax_rate, client_type = tax_rates[callback.data]
    
    await state.update_data(tax_rate=tax_rate, client_type=client_type)
    
    await callback.message.edit_text(
        f"💼 <b>Работа с {client_type}</b>\n"
        f"📊 Ставка налога: {tax_rate*100}%\n\n"
        "Введите ваш доход за месяц (в рублях):\n"
        "Пример: 50000"
    )
    
    await state.set_state(SelfEmployedStates.waiting_for_income_amount)
    await callback.answer()

@self_employed_router.message(SelfEmployedStates.waiting_for_income_amount)
async def calculate_self_employed(message: Message, state: FSMContext):
    if not message.text:
        return
        
    try:
        income = float(message.text)
        if income <= 0:
            await message.answer("❌ Доход должен быть положительным числом. Введите снова:")
            return
        
        user_data = await state.get_data()
        tax_rate = user_data['tax_rate']
        client_type = user_data['client_type']
        
        tax = income * tax_rate
        net_income = income - tax
        
        annual_income = income * 12
        limit_warning = ""
        if annual_income > 2400000:
            limit_warning = f"⚠️ <b>Внимание:</b> Годовой доход ({annual_income:,.0f}₽) превышает лимит для самозанятых (2.4 млн ₽/год)\n\n"
        
        # Сохраняем расчет в базу
        calculation = await db.save_calculation(
            user_id=message.from_user.id,
            calc_type="self_employed",
            income=income,
            expenses=0,
            result_data={
                "tax": tax,
                "net_income": net_income,
                "tax_rate": tax_rate,
                "client_type": client_type,
                "annual_income": annual_income,
                "limit_warning": annual_income > 2400000,
                "calculation_type": "Самозанятый"
            },
            additional_data={
                "client_type": client_type,
                "tax_rate": tax_rate
            }
        )
        
        await message.answer(
            f"👤 <b>Результат расчета для самозанятых:</b>\n\n"
            f"{limit_warning}"
            f"• Клиенты: {client_type}\n"
            f"• Доход в месяц: {income:,.0f}₽\n"
            f"• Ставка налога: {tax_rate*100}%\n"
            f"• Налог к уплате: {tax:,.0f}₽\n"
            f"• Чистый доход: {net_income:,.0f}₽\n\n"
            f"<i>Налог уплачивается через приложение 'Мой налог'</i>"
        )
        
        keyboard = get_callback_btns(
            btns={
                "🔄 Новый расчет": "new_self_employed",
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
        await message.answer("❌ Пожалуйста, введите число. Пример: 50000")