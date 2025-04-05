
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="O‘quvchilar 📚",callback_data='oqituvchi'),
            InlineKeyboardButton(text="Dars jadvali 📆",callback_data='jadval'),
        ],
        [
            InlineKeyboardButton(text="To‘lovlar 💰",callback_data="tolov"),
            InlineKeyboardButton(text="Xabarnomalar 📢",callback_data="xabar"),
        ],
        [
            InlineKeyboardButton(text="Sozlamalar ⚙️",callback_data="sozlama"),
        ],
    ]
)


boshqarish_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ O‘quvchi qo‘shish",callback_data='qoshish'),
            InlineKeyboardButton(text="🗑 O‘quvchini o‘chirish",callback_data='ochirish'),
        ],
        [
            InlineKeyboardButton(text="📋 O‘quvchilar ro‘yxati",callback_data="royxat"),
            InlineKeyboardButton(text="📊 O‘quvchi ma’lumotlari  ",callback_data="malumot"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga ",callback_data="orqaga"),
        ],
    ]
)



dars_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🗓 Jadvalni ko‘rish ",callback_data='korish'),
            InlineKeyboardButton(text="➕ Yangi dars qo‘shish ",callback_data='dars_qoshish'),
        ],
        [
            InlineKeyboardButton(text="🗑 Darsni o‘chirish ",callback_data="dars_ochirish"),
            InlineKeyboardButton(text="🔄 Jadvalni yangilash",callback_data="jadval_yangilash"),
        ],
        [
            InlineKeyboardButton("🗑️ Eski darslarni o‘chirish", callback_data="old_dars_ochirish")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga ",callback_data="orqaga"),
        ],
    ]
)



tolov_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 To‘lov qo‘shish",callback_data='tolov_qoshish'),
            InlineKeyboardButton(text="📊 To‘lovlar tarixi",callback_data='tolov_tarixi'),
        ],
        [
            InlineKeyboardButton(text="💳 To‘lov holati",callback_data="tolov_holati"),
            InlineKeyboardButton(text="🚨 Qarzdorlarni ko‘rish",callback_data="qarzni_korish"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga ",callback_data="orqaga"),
        ],
    ]
)


xabar_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📢 Umumiy xabar yuborish ",callback_data='umumiy_xabar'),
            InlineKeyboardButton(text="🎯 Ma’lum guruhga xabar",callback_data='guruxga_xabar'),
        ],
        [
            InlineKeyboardButton(text="👤 Ma’lum o‘quvchiga xabar",callback_data="malum_oquvchiga_xabar"),
            InlineKeyboardButton(text="📬 Yuborilgan xabarlar",callback_data="yuboril_xabar"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga ",callback_data="orqaga"),
        ],
    ]
)


sozlama_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Adminlar ro‘yxati",callback_data='admin_roxati'),
            InlineKeyboardButton(text="➕ Admin qo‘shish ",callback_data='admin_qosh'),
        ],
        [
            InlineKeyboardButton(text="🗑 Adminni o‘chirish ",callback_data="adminni_och"),
            InlineKeyboardButton(text="📊 Statistika ",callback_data="admin_static"),
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga ",callback_data="orqaga"),
        ],
    ]
)


orqa_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Orqaga ",callback_data="orqaga"),
        ],
    ]
)
