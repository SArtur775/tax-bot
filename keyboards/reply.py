# keyboards/reply.py
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_keyboard(
    *btns: str,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: tuple[int] = (2,),
):
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )

def get_main_menu():
    return get_keyboard(
        "🧮 Калькуляторы",           # Более понятный эмодзи
        "💰 Вычеты",                 # Короче и яснее
        "📅 Отчетность",             # Короче
        "👤 Самозанятые",            # Уже хорошо
        "⚙️ Настройки",              # Вместо "🔔 Напоминания"
        sizes=(2, 2, 1)
    )

def get_main_menu():
    return get_keyboard(
        "🧮 Калькуляторы",     # НОВЫЙ текст
        "💰 Вычеты", 
        "📅 Отчетность",
        "👤 Самозанятые",
        "⚙️ Настройки",
        sizes=(2, 2, 1)
    )

def get_calculators_menu():
    return get_keyboard(
        "💼 НДФЛ 13%",     # НОВЫЙ текст
        "📊 УСН 6%", 
        "📈 УСН 15%",
        "👤 Самозанятый",
        "🔙 Назад",
        sizes=(2, 2, 1)
    )