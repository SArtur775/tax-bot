# keyboards/main_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 Калькулятор налогов")],
            [KeyboardButton(text="💰 Налоговые вычеты")],
            [KeyboardButton(text="📅 Сроки отчетности")],
            [KeyboardButton(text="👤 Помощь самозанятым")],
            [KeyboardButton(text="🔔 Напоминания")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )