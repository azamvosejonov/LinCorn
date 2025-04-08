
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

user_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📚 Mening darslarim",callback_data='jadvallimi'),
            InlineKeyboardButton(text="💰 Mening to‘lovlarim ",callback_data='mening_tol'),
        ],
        [
            InlineKeyboardButton(text="📆 Jadvalim",callback_data="jadvallim"),
            InlineKeyboardButton(text="📢 E’lonlar ",callback_data="elonlar"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Yordam",callback_data="yordamlar"),
        ],
    ]
)


darslar_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🗓 Dars jadvalini ko‘rish",callback_data='jadvallimi'),
            InlineKeyboardButton(text="📖 O‘tgan darslar ",callback_data='otgan_dars'),
        ],
        [
            InlineKeyboardButton(text="🔄 Yangilash ", callback_data="jadvallim"),
            InlineKeyboardButton(text="🔙 Orqaga",callback_data="orqali"),
        ],
    ]
)



tolovlar_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 To‘lov holati",callback_data='tolovlar_h'),
            InlineKeyboardButton(text="📜 To‘lovlar tarixi",callback_data='tolov_t'),
        ],
        [
            InlineKeyboardButton(text="💵 To‘lov qilish   ",callback_data="tolov_q"),
            InlineKeyboardButton(text="🔄 Yangilash   ",callback_data="mening_tol"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="orqali"),
        ],
    ]
)

xabarlar_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📬 So‘nggi e’lonlar",callback_data='songi_e'),
            InlineKeyboardButton(text="🛠 Foydalanish bo‘yicha qo‘llanma",callback_data='qollanma'),
        ],
        [
            InlineKeyboardButton(text="📞 Bog‘lanish",callback_data="qollab_quvvatlash"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="orqali"),
        ],
    ]
)


yordam_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❓ Savollar va javoblar ",callback_data='s_javoblar'),
            InlineKeyboardButton(text="📞 Qo‘llab-quvvatlash",callback_data='qollab_quvvatlash'),
        ],
        [
            InlineKeyboardButton(text="📜 Bot haqida",callback_data="bot_h"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="orqali"),
        ],
    ]
)


orqasi_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="orqali"),
        ],
    ]
)



