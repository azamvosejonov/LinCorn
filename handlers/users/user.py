from keyboards.inline.user import yordam_inline
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import CallbackQuery
from loader import dp,bot,jadval_db,user_db,pyment_db
from states.states import oquvchi_qo,oquvchi_o,oquvchi_r,AddJadval,UpdateJadval,TolovStates
from keyboards.default.status import oquvchi_button
from keyboards.inline.user import tolovlar_inline,user_inline,darslar_inline,orqa_inline
from aiogram.dispatcher.filters import Text




@dp.callback_query_handler(text='jadvallim')
async def korish_jadval(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Jadvallar",reply_markup=darslar_inline)

@dp.callback_query_handler(lambda c: c.data == 'jadvallimi')
async def korish_jadval(call: CallbackQuery):
    jadval_list = jadval_db.get_upcoming_lessons()  # Faqat kelgusi darslarni olish
    if not jadval_list:
        await call.message.answer("📭 Kelgusi darslar mavjud emas!")
        return

    text = "📋 <b>Kelayotgan darslar:</b>\n"
    for jadval in jadval_list:
        text += (f"\n🔹 <b>ID:</b> {jadval[0]}\n"
                 f"📌 <b>Sarlavha:</b> {jadval[1]}\n"
                 f"⏳ <b>Boshlanish:</b> {jadval[2]}\n"
                 f"⏰ <b>Tugash:</b> {jadval[3]}\n")

    await call.message.answer(text, parse_mode="HTML",reply_markup=orqa_inline)



@dp.callback_query_handler(lambda c: c.data == 'yordamlar')
async def korish_jadval(call: CallbackQuery):
    await call.message.answer("Yordamlar",reply_markup=yordam_inline)

@dp.callback_query_handler(lambda c: c.data == 's_javoblar')
async def korish_jadval(call: CallbackQuery):
    await call.message.answer("Telegram adminga murojat qiling: @azam_vosejonov",reply_markup=orqa_inline)

@dp.callback_query_handler(lambda c: c.data == 'qollab_quvvatlash')
async def korish_jadval(call: CallbackQuery):
    await call.message.answer("Murojat uchun telefon raqam: 990232323",reply_markup=orqa_inline)

@dp.callback_query_handler(lambda c: c.data == 'bot_h')
async def korish_jadval(call: CallbackQuery):
    await call.message.answer("Bot lin cor",reply_markup=orqa_inline)


@dp.callback_query_handler(lambda c: c.data == 'elonlar')
async def show_user_messages(call: CallbackQuery):
    telegram_id = call.from_user.id  # Foydalanuvchining Telegram ID sini olish
    messages = user_db.get_messages_by_telegram_id(telegram_id)  # Xabarlarni olish

    if not messages:
        await call.message.answer("📭 Sizga yuborilgan hech qanday xabar mavjud emas.")
        return

    text = "📩 <b>Sizga yuborilgan xabarlar:</b>\n"
    for message, sent_at in messages:
        text += f"\n🕰 {sent_at}\n📩 {message}\n"

    await call.message.answer(text, parse_mode="HTML",reply_markup=orqa_inline)



@dp.callback_query_handler(lambda c: c.data == 'mening_tol')
async def korish_jadval(call: CallbackQuery):
    await call.message.answer("Mening to'lovlarim",reply_markup=tolovlar_inline)


@dp.callback_query_handler(text='tolovlar_h')
async def check_user_status(call: CallbackQuery):
    """Foydalanuvchining statusini tekshiruvchi callback handler"""
    telegram_id = call.from_user.id
    user_status = user_db.get_student_statusi(telegram_id)

    if user_status == "faol":
        await call.message.answer("✅ Siz faol foydalanuvchisiz. Qarzingiz yo‘q!",reply_markup=orqa_inline)
    elif user_status:
        await call.message.answer(f"❌ Siz {user_status} holatidasiz. Iltimos, to‘lov qiling!",reply_markup=orqa_inline)
    else:
        await call.message.answer("⚠️ Siz ro‘yxatdan o‘tmagansiz yoki ma’lumotlar bazada topilmadi.",reply_markup=orqa_inline)

@dp.callback_query_handler(lambda c: c.data == 'otgan_dars')
async def show_past_lessons_one_day(call: CallbackQuery):
    # So‘nggi 1 kun ichida o‘tgan darslarni olish
    past_lessons = jadval_db.get_past_lessons_last_1_day()

    if not past_lessons:
        await call.message.answer("📭 So‘nggi 1 kun ichida o‘tgan dars mavjud emas!")
        return

    text = "📋 <b>So‘nggi 1 kun ichida o‘tgan darslar:</b>\n"
    for jadval in past_lessons:
        text += (f"\n🔹 <b>ID:</b> {jadval[0]}\n"
                 f"📌 <b>Sarlavha:</b> {jadval[1]}\n"
                 f"⏳ <b>Boshlanish:</b> {jadval[2]}\n"
                 f"⏰ <b>Tugash:</b> {jadval[3]}\n")

    await call.message.answer(text, parse_mode="HTML",reply_markup=orqa_inline)

@dp.callback_query_handler(lambda c: c.data == 'old_dars_ochirish')
async def delete_old_lessons_handler(call: CallbackQuery):
    """1 soatdan ortiq vaqt bo‘lgan darslarni qo‘lda o‘chirish"""
    jadval_db.delete_old_lessons()
    await call.message.answer("✅ 1 soatdan oshgan eski darslar o‘chirildi!",reply_markup=orqa_inline)


@dp.callback_query_handler(text="qollanma")
async def qollanma(call: CallbackQuery):
    await call.message.answer("Botdan",reply_markup=orqa_inline)

@dp.callback_query_handler(text="orqali")
async def orqali(call: CallbackQuery):
    await call.message.answer("Bosh tugamlar",reply_markup=user_inline)







