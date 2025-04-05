from aiogram.types import ReplyKeyboardMarkup,KeyboardButton
menu_button=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Ha"),
            KeyboardButton(text="Yo`q"),
        ]
    ],
    resize_keyboard = True,
    one_time_keyboard=True

)


oquvchi_button=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅To`gri"),
            KeyboardButton(text="❌No`to`g`ri"),
        ]
    ],
    resize_keyboard = True,
    one_time_keyboard = True
)

start_button=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Boshqatdan ariza berish"),
        ]
    ],resize_keyboard = True
)

