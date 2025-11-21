# keyboards/calculators_menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_calculators_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="НДФЛ 13%")],
            [KeyboardButton(text="УСН 6%")],
            [KeyboardButton(text="УСН 15%")],
            [KeyboardButton(text="Самозанятый 4-6%")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )