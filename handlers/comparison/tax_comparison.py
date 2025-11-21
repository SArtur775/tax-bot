# handlers/comparison/tax_comparison.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards.reply import get_main_menu
from keyboards.inline import get_callback_btns
from config import db

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

# Основная функция расчета сравнения
async def calculate_comparison(message: Message, state: FSMContext):
    user_data = await state.get_data()
    income = user_data['income']
    expenses = user_data.get('expenses', 0)
    activity_type = user_data['activity_type']
    
    # Расчет налогов для каждой системы
    results = await calculate_all_tax_systems(income, expenses, activity_type)
    
    # Формируем сравнительную таблицу
    comparison_table = await create_comparison_table(results)
    
    # Отправляем результаты
    await message.answer(comparison_table)
    
    # Рекомендация оптимальной системы
    best_system = await find_best_system(results)
    await message.answer(
        f"🎯 <b>Рекомендуемая система:</b> {best_system['name']}\n"
        f"💵 <b>Налог в месяц:</b> {best_system['monthly_tax']:,.0f}₽\n"
        f"📈 <b>Экономия в год:</b> {best_system['yearly_saving']:,.0f}₽",
        reply_markup=get_main_menu()
    )
    
    # --- СОХРАНЕНИЕ В БАЗУ ДАННЫХ ---
    try:
        result_data = {
            'results': results,
            'best_system': best_system,
            'activity_type': activity_type
        }
        await db.save_calculation(
            user_id=message.from_user.id,
            calc_type="comparison",
            income=income,
            expenses=expenses,
            result_data=result_data
        )
    except Exception as e:
        print(f"Ошибка сохранения сравнения: {e}")
    # --- КОНЕЦ СОХРАНЕНИЯ ---
    
    await state.clear()

async def calculate_all_tax_systems(income: float, expenses: float, activity_type: str) -> dict:
    """Расчет налогов для всех систем"""
    monthly_income = income
    yearly_income = income * 12
    
    results = {}
    
    # 1. НДФЛ 13%
    results['ndfl'] = {
        'name': 'НДФЛ 13%',
        'monthly_tax': monthly_income * 0.13,
        'yearly_tax': yearly_income * 0.13,
        'available': activity_type in ['employee']
    }
    
    # 2. УСН 6%
    results['usn6'] = {
        'name': 'УСН 6%',
        'monthly_tax': monthly_income * 0.06,
        'yearly_tax': yearly_income * 0.06,
        'available': activity_type in ['freelancer', 'business']
    }
    
    # 3. УСН 15%
    if activity_type in ['business', 'freelancer']:
        tax_base = max(0, monthly_income - expenses)
        tax = tax_base * 0.15
        # Минимальный налог 1%
        min_tax = monthly_income * 0.01
        actual_tax = max(tax, min_tax)
        
        results['usn15'] = {
            'name': 'УСН 15%',
            'monthly_tax': actual_tax,
            'yearly_tax': actual_tax * 12,
            'available': activity_type in ['business', 'freelancer']
        }
    
    # 4. Самозанятый
    tax_rate = 0.06 if activity_type in ['business', 'freelancer'] else 0.04
    yearly_income_limit = yearly_income <= 2400000
    
    results['self_employed'] = {
        'name': 'Самозанятый',
        'monthly_tax': monthly_income * tax_rate,
        'yearly_tax': yearly_income * tax_rate,
        'available': activity_type in ['self_employed', 'freelancer'] and yearly_income_limit
    }
    
    return results

async def create_comparison_table(results: dict) -> str:
    """Создание сравнительной таблицы"""
    table = "📊 <b>Сравнение налоговых систем</b>\n\n"
    
    for system_id, data in results.items():
        if data['available']:
            status = "✅ Доступно"
            monthly_tax = f"{data['monthly_tax']:,.0f}₽"
            yearly_tax = f"{data['yearly_tax']:,.0f}₽"
        else:
            status = "❌ Недоступно"
            monthly_tax = "—"
            yearly_tax = "—"
            
        table += (
            f"<b>{data['name']}</b> {status}\n"
            f"   💰 Налог в месяц: {monthly_tax}\n"
            f"   📅 Налог в год: {yearly_tax}\n\n"
        )
    
    return table

async def find_best_system(results: dict) -> dict:
    """Поиск оптимальной системы налогообложения"""
    available_systems = {k: v for k, v in results.items() if v['available']}
    
    if not available_systems:
        return {
            'name': 'Подходящая система не найдена',
            'monthly_tax': 0, 
            'yearly_saving': 0
        }
    
    # Система с минимальным налогом
    best_system_id = min(available_systems.keys(), 
                        key=lambda x: available_systems[x]['monthly_tax'])
    best_system = available_systems[best_system_id]
    
    # Расчет экономии относительно максимального налога
    if len(available_systems) > 1:
        max_tax = max(system['monthly_tax'] for system in available_systems.values())
        yearly_saving = (max_tax - best_system['monthly_tax']) * 12
    else:
        yearly_saving = 0
    
    return {
        'name': best_system['name'],
        'monthly_tax': best_system['monthly_tax'],
        'yearly_saving': yearly_saving
    }