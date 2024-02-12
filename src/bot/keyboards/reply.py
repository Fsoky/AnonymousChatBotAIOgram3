from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

rmk = ReplyKeyboardRemove()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="☕ Искать собеседника")]
    ],
    resize_keyboard=True
)