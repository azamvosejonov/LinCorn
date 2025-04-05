from keyboards.inline.admin import admin_inline
from keyboards.inline.user import user_inline
from aiogram.dispatcher import FSMContext
from data.config import ADMINS
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.default.status import menu_button
from aiogram import types
from loader import dp,user_db,admin_db
from states.states import next_quiz
ADMIN=[7126357860]


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user_db.create_table_messages()
    telegram_id = message.from_user.id

    # Foydalanuvchi admin ekanligini tekshiramiz
    if telegram_id in ADMIN or admin_db.is_admin(telegram_id):
        await message.answer("👮‍♂️ Siz bot adminisiz!", reply_markup=admin_inline)
        return

    # Agar foydalanuvchi ro‘yxatdan o‘tmagan bo‘lsa
    if not user_db.select_student(telegram_id=telegram_id):
        text = (
            "👋 Assalomu alaykum, siz LinCor botga ariza berdingiz.\n\n"
            "📋 Hozir siz bir necha savollarga javob berasiz.\n"
            "✅ Har biriga javob bering.\n"
            "🔹 Oxirida agar hammasi to‘g‘ri bo‘lsa, **HA** tugmasini bosing va "
            "arizangiz adminga yuboriladi."
        )
        await message.answer(text, parse_mode="Markdown")
        await message.answer("📌 *Ism, familiyangizni kiriting?*", parse_mode="Markdown")
        await next_quiz.keyingi.set()
        return

    # Agar foydalanuvchi oddiy user bo‘lsa
    await message.answer("✅ Siz botdan foydalanishingiz mumkin!", reply_markup=user_inline)






@dp.message_handler(state=next_quiz.keyingi)
async def ism_familyasi(message: types.Message, state: FSMContext):
    ism_familya=message.text
    await state.update_data(
        {
            "ism_familya": ism_familya,
        }
    )
    await next_quiz.keyingisi.set()
    text=f"🕑 Yosh:"
    text+=f"Yoshingizni kiriting?"
    text+=f"<b>Masalan, 19?</b>"
    await message.answer(text)

@dp.message_handler(state=next_quiz.keyingisi)
async def yosh_state(message: types.Message, state: FSMContext):
    yoshi = message.text
    await state.update_data(
        {
            "yoshi": yoshi,
        }
    )
    await next_quiz.tel.set()
    text=f"📞Telefon raqmingiz:\n\n"
    text+=f"Telefon raqamingizni kiriting.\n\n"
    text+=f"<i> Masalan:+998 90 123 45 67</i>"
    await message.answer(text)
@dp.message_handler(state=next_quiz.tel)
async def texno_state(message: types.Message, state: FSMContext):
    tel = message.text
    await state.update_data(
        {
            "tel": tel,
        }
    )
    await next_quiz.grux.set()
    tel=f"Grux id sini kiriting "
    tel+=f"Masalan,12 "
    await message.answer(tel)
@dp.message_handler(state=next_quiz.grux)
async def aloqa_state(message: types.Message, state: FSMContext):
    grux = message.text
    await state.update_data(
        {
            "grux": grux,
        }
    )
    user_data = await state.get_data()
    ism_familiya = user_data.get('ism_familya')
    yoshi = user_data.get('yoshi')
    tel = user_data.get('tel')
    grux = user_data.get('grux')

    text = f"Adminga ariza:\n\n"
    text += f"👨‍💼 Isim Familya:{ism_familiya}\n"
    text += f"🕑 Yosh:{yoshi}\n"
    text += f"📞Telefon raqam:{tel}\n"
    text += f"🇺🇿 Telegram:@{message.from_user.username}\n"
    text += f"🆔Grux id:{grux}\n"

    await message.answer(text)
    await message.answer("Barcha ma'lumotlar to'g'rimi?", reply_markup=menu_button)
    await next_quiz.status.set()


@dp.message_handler(state=next_quiz.status)
async def ha_choice(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text=="Ha":
        for admin in ADMINS:
            await dp.bot.send_message(
                admin,
                "Ariza:\n\n"
                f"👨‍💼 Ism Familyasi: {user_data.get('ism_familya')}\n"
                f"🕑 Yosh: {user_data.get('yoshi')}\n"
                f"📞Telefon raqam: {user_data.get('tel')}\n"
                f"🪪Grux id: {user_data.get('grux')}\n"
                f"🆔Telegram id: {message.from_user.id}"
            )
        await message.answer("So'rov adminga yuborildi.")
        await state.finish()
    elif message.text=="Yo`q":
        await message.answer("Bekor qilindi!")
        await state.finish()




