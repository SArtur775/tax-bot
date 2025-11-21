# handlers/history/history_handler.py
from aiogram import Router, types
from aiogram.filters import Command
from keyboards.reply import get_main_menu
from config import db

router = Router()

@router.message(Command("history"))
async def show_history(message: types.Message):
    try:
        user_id = message.from_user.id
        calculations = await db.get_user_calculations(user_id, limit=10)
        
        if not calculations:
            await message.answer(
                "📝 У вас еще нет сохраненных расчетов.\n\n"
                "Начните с калькуляторов или сравнения систем!",
                reply_markup=get_main_menu()
            )
            return
        
        text = "📊 <b>История ваших расчетов:</b>\n\n"
        
        for i, calc in enumerate(calculations, 1):
            type_names = {
                "ndfl": "🧾 НДФЛ",
                "usn6": "📊 УСН 6%", 
                "usn15": "📈 УСН 15%",
                "self_employed": "👤 Самозанятый",
                "comparison": "🔍 Сравнение систем"
            }
            
            emoji = "🟢" if calc.calc_type == "comparison" else "🔵"
            text += f"{emoji} <b>{type_names[calc.calc_type]}</b>\n"
            text += f"   💰 Доход: {calc.income:,.0f}₽\n"
            
            if calc.expenses > 0:
                text += f"   📉 Расходы: {calc.expenses:,.0f}₽\n"
            
            text += f"   📅 {calc.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        
        await message.answer(text, reply_markup=get_main_menu())
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка загрузки истории: {str(e)}",
            reply_markup=get_main_menu()
        )