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
    '''
    Parameters request_contact and request_location must be as indexes of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине", 
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона"
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
    '''
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):
        
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)

# ======== КОНКРЕТНЫЕ REPLY КЛАВИАТУРЫ ========

def get_main_reply_menu():
    return get_keyboard(
        "🔄 Калькулятор налогов",
        "💰 Налоговые вычеты", 
        "📅 Сроки отчетности",
        "👤 Помощь самозанятым",
        "🔔 Напоминания",
        sizes=(2, 2, 1)
    )

def get_calculators_reply_menu():
    return get_keyboard(
        "НДФЛ 13%",
        "УСН 6%",
        "УСН 15%", 
        "Самозанятый 4-6%",
        "🔙 Назад в главное меню",
        sizes=(2, 2, 1)
    )