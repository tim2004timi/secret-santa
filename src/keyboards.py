from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

menu_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👕 Косплей", callback_data="cosplay-menu"),
            InlineKeyboardButton(text="🎁 Подарок", callback_data="gift"),
        ],
    ]
)
