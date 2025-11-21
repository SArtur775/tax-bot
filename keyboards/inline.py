# keyboards/inline.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_callback_btns(
    *, 
    btns: dict[str, str], 
    sizes: tuple[int] = (2,)
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()

# ======== КОНКРЕТНЫЕ INLINE КЛАВИАТУРЫ ========

def get_calculators_inline_menu():
    return get_callback_btns(
        btns={
            "🧮 НДФЛ 13%": "calc_ndfl",
            "📊 УСН 6%": "calc_usn6", 
            "📈 УСН 15%": "calc_usn15",
            "👤 Самозанятый": "calc_self_employed"
        },
        sizes=(2, 2)
    )

def get_back_inline():
    return get_callback_btns(
        btns={"🔙 Назад": "back_to_main"},
        sizes=(1,)
    )