# handlers/comparison/tax_comparison.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_main_menu
from keyboards.inline import get_callback_btns

comparison_router = Router()

class ComparisonStates(StatesGroup):
    waiting_for_income = State()
    waiting_for_expenses = State()
    waiting_for_activity_type = State()

# Запуск системы сравнения
@comparison_router.message(F.text == "📊 Сравнить системы")
async def start_comparison(message: Message, state: FSMContext):
    keyboard = get_callback_btns(
        btns={
            "💼 Наемный работник": "employee",
            "👨‍💼 Фрилансер/ИП": "freelancer", 
            "🏢 Бизнес с расходами": "business",
            "👤 Самозанятый": "self_employed"
        },
        sizes=(2, 2)
    )
    
    await message.answer(
        "🔍 <b>Сравнение налоговых систем</b>\n\n"
        "Выберите ваш тип деятельности:",
        reply_markup=keyboard
    )

# Обработчик выбора типа деятельности
@comparison_router.callback_query(F.data.in_(["employee", "freelancer", "business", "self_employed"]))
async def process_activity_type(callback: CallbackQuery, state: FSMContext):
    activity_types = {
        "employee": "наемный работник",
        "freelancer": "фрилансер/ИП",
        "business": "бизнес с расходами", 
        "self_employed": "самозанятый"
    }
    
    await state.update_data(activity_type=callback.data)
    
    await callback.message.edit_text(
        f"💼 <b>Тип:</b> {activity_types[callback.data]}\n\n"
        "Введите ваш ожидаемый месячный доход (в рублях):\n"
        "Пример: 100000"
    )
    
    await state.set_state(ComparisonStates.waiting_for_income)
    await callback.answer()

# Обработчик ввода дохода
@comparison_router.message(ComparisonStates.waiting_for_income)
async def process_income(message: Message, state: FSMContext):
    try:
        income = float(message.text)
        if income <= 0:
            await message.answer("❌ Доход должен быть положительным числом. Введите снова:")
            return
        
        await state.update_data(income=income)
        
        user_data = await state.get_data()
        activity_type = user_data['activity_type']
        
        if activity_type in ["business", "freelancer"]:
            await message.answer(
                f"✅ Доход: {income:,.0f}₽/месяц\n\n"
                "Введите ваши ожидаемые месячные расходы (в рублях):\n"
                "Пример: 30000\n"
                "Если расходов нет, введите 0"
            )
            await state.set_state(ComparisonStates.waiting_for_expenses)
        else:
            # Для работников и самозанятых сразу считаем
            await calculate_comparison(message, state)
            
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число. Пример: 100000")

# Обработчик ввода расходов (для бизнеса)
@comparison_router.message(ComparisonStates.waiting_for_expenses)
async def process_expenses(message: Message, state: FSMContext):
    try:
        expenses = float(message.text)
        if expenses < 0:
            await message.answer("❌ Расходы не могут быть отрицательными. Введите снова:")
            return
        
        await state.update_data(expenses=expenses)
        await calculate_comparison(message, state)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число. Пример: 30000")

# Функция расчета сравнения (пока заглушка)
async def calculate_comparison(message: Message, state: FSMContext):
    user_data = await state.get_data()
    
    await message.answer(
        "🔄 <b>Расчет сравнения налоговых систем...</b>\n\n"
        "Эта функция находится в разработке.\n"
        "Скоро здесь будет детальное сравнение всех систем налогообложения!",
        reply_markup=get_main_menu()
    )
    
    await state.clear()