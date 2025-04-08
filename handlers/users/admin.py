from datetime import datetime

from keyboards.inline.admin import boshqarish_inline, dars_inline, tolov_inline, sozlama_inline, xabar_inline,admin_inline,orqa_inline
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import CallbackQuery
from loader import dp,bot,jadval_db,user_db,admin_db,pyment_db
from states.states import oquvchi_qo,oquvchi_o,oquvchi_r,AdminStates,AddJadval,UpdateJadval,TolovStates,Davomat,SendMessageState
from keyboards.default.status import oquvchi_button
from aiogram.dispatcher.handler import CancelHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from keyboards.inline.user import orqasi_inline





#-----------------------------O`QUVCHI------------------------------------------------------
@dp.callback_query_handler(text='oqituvchi')
async def oqtuvchi_malumotlar(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Barcha ma'lumotlar!", reply_markup=boshqarish_inline)


@dp.callback_query_handler(text='qoshish')
async def oquvchi_q(call: CallbackQuery):
    await oquvchi_qo.ism.set()
    await call.message.delete()
    await call.message.answer("O‘quvchi ism-sharifini kiriting!")


@dp.message_handler(state=oquvchi_qo.ism)
async def ism_familyasi(message: types.Message, state: FSMContext):
    ism_familya = message.text
    await state.update_data(ism_familya=ism_familya)

    text = "🕑 Yoshingizni kiriting:\n<b>Masalan, 19</b>"
    await message.answer(text)
    await oquvchi_qo.yosh.set()


@dp.message_handler(state=oquvchi_qo.yosh)
async def yosh_state(message: types.Message, state: FSMContext):
    yoshi = message.text
    if not yoshi.isdigit():
        await message.answer("Iltimos, yoshingizni faqat raqam sifatida kiriting.")
        return

    await state.update_data(yoshi=yoshi)

    text = "📞 Telefon raqamingizni kiriting:\n<i>Masalan: +998 90 123 45 67</i>"
    await message.answer(text)
    await oquvchi_qo.tel.set()


@dp.message_handler(state=oquvchi_qo.tel)
async def tel_state(message: types.Message, state: FSMContext):
    tel = message.text
    await state.update_data(tel=tel)

    text = "📌 Guruh nomini kiriting:\n<b>Masalan, Koreys tili</b>"
    await message.answer(text)
    await oquvchi_qo.gruhi.set()


@dp.message_handler(state=oquvchi_qo.gruhi)
async def gruhi_state(message: types.Message, state: FSMContext):
    grux = message.text

    await state.update_data(gruhi=grux)
    await message.answer("Telegram idni kiriting!")
    await oquvchi_qo.o_id.set()

@dp.message_handler(state=oquvchi_qo.o_id)
async def gruhi_state(message: types.Message, state: FSMContext):
    o_id = message.text
    await state.update_data(o_id=o_id)

    user_data = await state.get_data()
    username = message.from_user.username if message.from_user.username else "Noma’lum"

    text = (f"📌 <b>Adminga ariza</b>:\n\n"
            f"👨‍💼 Ism Familiya: {user_data['ism_familya']}\n"
            f"🕑 Yosh: {user_data['yoshi']}\n"
            f"📞 Telefon: {user_data['tel']}\n"
            f"🇺🇿 Telegram: @{username}\n"
            f"🆔 Guruh ID: {user_data['gruhi']}\n\n"
            "Barcha ma'lumotlar to‘g‘rimi?")

    await message.answer(text, reply_markup=oquvchi_button)
    await oquvchi_qo.tanlash.set()


@dp.message_handler(state=oquvchi_qo.tanlash)
async def tanlash_state(message: types.Message, state: FSMContext):
    if message.text=="✅To`gri":
        user_data = await state.get_data()
        try:
            user_db.add_student(
                full_name=user_data['ism_familya'],
                yosh=int(user_data['yoshi']),
                phone=user_data['tel'],
                group_id=user_data['gruhi'],
                telegram_id=int(user_data['o_id'])
            )
            await message.answer(f"O‘quvchi muvaffaqqiyatli qo‘shildi!\nGuruh nomi: {user_data['gruhi']}",reply_markup=orqa_inline)
            await state.finish()
        except Exception as e:
            await message.answer(f"Xatolik yuz berdi: {e}")
    elif message.text=="❌No`to`g`ri":
        await message.answer("Bekor qilindi!",reply_markup=orqa_inline)
        await state.finish()


@dp.callback_query_handler(text='ochirish')
async def oqtuvchi_malumotlar(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Ism-familyasini to`g`ri kiriting bo`lmasa o`chirilmaydi‼️")
    await oquvchi_o.ism.set()

@dp.message_handler(state=oquvchi_o.ism)
async def ism_familyasi(message: types.Message, state: FSMContext):
    ism_familya = message.text
    await state.update_data(ism_familya=ism_familya)
    await message.answer("Grux nomini kiriting!")
    await oquvchi_o.grux_id.set()

@dp.message_handler(state=oquvchi_o.grux_id)
async def ism_familyasi(message: types.Message, state: FSMContext):
    id = message.text
    await state.update_data(id=id)
    user_data = await state.get_data()
    try:
        user_db.delete_student_postid(
            full_name=user_data['ism_familya'],
            group_id=user_data['id']
        )
        await message.answer(f"O‘quvchi o`chirilganini tekshirib ko`ring‼️\nAgar o`chirilmagan bo`lsa ism-famiyasida yoki guruhini no`to`g`ri kiritgansiz‼️",reply_markup=orqa_inline)
        await state.finish()
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")


@dp.callback_query_handler(text='malumot')
async def oqtuvchi_malumotlar(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Grux nomini kiriting!")
    await oquvchi_r.grux_id.set()

@dp.message_handler(state=oquvchi_r.grux_id)
async def ism_familyasi(message: types.Message, state: FSMContext):
    try:
        group_id = message.text
        await state.update_data(group_id=group_id)

        students = user_db.student_list(group_id)

        if students:
            response = "📋 **Guruhdagi talabalar:**\n\n"
            for student in students:
                full_name, phone, group_id, yosh = student  # Tuple elementlarini ajratish
                response += f"👤 Ism: {full_name}\n📞 Telefon: {phone}\n🎂 Yosh: {yosh}\n🏫 Guruh: {group_id}\n----------------------------\n\n"

            await bot.send_message(chat_id=message.chat.id, text=response,reply_markup=orqa_inline)
            await state.finish()
        else:
            await message.answer(f"Uzur, {group_id} nomi bilan hech qanday talaba topilmadi.",reply_markup=orqa_inline)
        await state.finish()
    except ValueError:
        await message.answer("❌ Iltimos, to'g'ri guruh ID kiriting! (faqat raqam)",reply_markup=orqa_inline)
        await state.finish()


@dp.callback_query_handler(text="royxat")
async def oqtuvchi_malumotlar(call: CallbackQuery):
    await call.message.delete()

    students = user_db.student_r()

    if not isinstance(students, list) or not students:
        await call.message.answer("📌 *Hozircha ma'lumotlar mavjud emas yoki noto‘g‘ri format!*",reply_markup=orqa_inline)
        return

    try:
        student_list = "\n".join(
            f"👤 *Ism Familyasi:* {student['full_name']}\n"
            f"🆔 *Guruh nomi:* {student['group_id']}\n"
            f"🎂 *Yoshi:* {student['yosh']}\n"
            f"📞 *Telefon raqami:* `{student['phone']}`\n"
            "➖➖➖➖➖➖➖➖➖"
            for student in students if isinstance(student, dict)  # Lug‘at bo‘lsa
        )
    except (KeyError, TypeError):
        await call.message.answer("⚠ Ma'lumotlar noto‘g‘ri formatda! Admin bilan bog‘laning.",reply_markup=orqa_inline)
        return

    message_text = f"📋 *Barcha mavjud ma'lumotlar:*\n\n{student_list}"
    await call.message.answer(message_text,reply_markup=orqa_inline)


@dp.callback_query_handler(text='davomat')
async def davomat_boshlash(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("📌 Davomat uchun guruh nomi kiriting:")
    await Davomat.grux_id.set()


@dp.message_handler(state=Davomat.grux_id)
async def davomat_guruh_kiritish(message: types.Message, state: FSMContext):


    await state.update_data(grux_id=message.text)
    await message.answer("👤 Talabaning ism-sharifini kiriting:")
    await Davomat.ism_familya.set()


@dp.message_handler(state=Davomat.ism_familya)
async def davomat_talaba_kiritish(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    group_id = user_data['grux_id']
    full_name = message.text

    student = user_db.get_student_by_name_and_group(full_name, group_id)
    if not student:
        await message.answer("❌ Bunday ism bilan talaba topilmadi!",reply_markup=orqa_inline)
        await state.finish()
        return

    student_id = student[0]
    user_db.mark_attendance(student_id, date=datetime.now().date(), status="present")

    await message.answer(f"✅ {full_name} davomatga qo‘shildi!",reply_markup=orqa_inline)
    await state.finish()


# 📌 Davomatni tekshirish (O‘qituvchi)
@dp.callback_query_handler(text='davomat_tekshirish')
async def davomat_tekshirish(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("📌 Davomatni tekshirish uchun guruh ID sini kiriting:")
    await Davomat.grux_id.set()


@dp.message_handler(state=Davomat.grux_id)
async def davomat_ko_rish(message: types.Message, state: FSMContext):
    try:
        group_id = message.text
        students = user_db.get_all_students()

        if not students:
            await message.answer(f"📌 {group_id} nomi bilan hech qanday talaba topilmadi.",reply_markup=orqa_inline)
            await state.finish()
            return

        response = "📋 **Guruhdagi davomat ro‘yxati:**\n\n"
        for student in students:
            student_id = student[0]
            full_name = student[1]
            absent_days = user_db.get_absent_days(student_id)
            response += f"👤 {full_name} | ❌ Davomatdan qolgan kunlar: {absent_days}\n"

        await message.answer(response)
        await state.finish()

    except ValueError:
        await message.answer("❌ Iltimos, to'g'ri guruh ID kiriting! (faqat raqam)",reply_markup=orqa_inline)
        await state.finish()


#---------------------------JADVAL-------------------------------------------------------------


@dp.callback_query_handler(text='jadval')
async def show_jadval_menu(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Barcha ma'lumotlar!", reply_markup=dars_inline)

@dp.callback_query_handler(lambda c: c.data == 'korish')
async def korish_jadval(call: CallbackQuery):
    await call.message.delete()

    jadval_list = jadval_db.get_jadval()

    if not jadval_list:
        await call.message.answer("📭 Jadvallar mavjud emas!",reply_markup=orqa_inline)
        return

    text = "📋 <b>Jadvallar:</b>\n"
    for jadval in jadval_list:
        text += (f"\n🔹 <b>ID:</b> {jadval[0]}\n"
                 f"📌 <b>Sarlavha:</b> {jadval[1]}\n"
                 f"📅 <b>Sana:</b> {jadval[2]}\n"
                 f"⏳ <b>Boshlanish:</b> {jadval[3]}\n"
                 f"⏰ <b>Tugash:</b> {jadval[4]}\n")
    await call.message.answer(text,reply_markup=orqa_inline)


@dp.callback_query_handler(lambda c: c.data == 'dars_qoshish')
async def dars_qoshish(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("📝 Yangi dars qo‘shish uchun, sarlavhani kiriting:")
    await AddJadval.title.set()


@dp.message_handler(state=AddJadval.title)
async def set_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("⏳ Endi boshlanish vaqtini kiriting (HH:MM formatda):")
    await AddJadval.next()


@dp.message_handler(state=AddJadval.start_time)
async def set_start_time(message: types.Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%H:%M")
        await state.update_data(start_time=message.text)
        await message.answer("⏰ Endi tugash vaqtini kiriting (HH:MM formatda):")
        await AddJadval.next()
    except ValueError:
        await message.answer("⚠️ Iltimos, vaqtni HH:MM formatida kiriting!")


@dp.message_handler(state=AddJadval.end_time)
async def set_end_time(message: types.Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%H:%M")
        await state.update_data(end_time=message.text)
        await message.answer("📅 Dars sanasini kiriting (YYYY-MM-DD yoki MM-DD formatda):")
        await AddJadval.next()
    except ValueError:
        await message.answer("⚠️ Iltimos, vaqtni HH:MM formatida kiriting!")


@dp.message_handler(state=AddJadval.date)
async def set_date(message: types.Message, state: FSMContext):
    try:
        today = datetime.today()
        parts = message.text.split("-")

        if len(parts) == 3:
            date = datetime.strptime(message.text, "%Y-%m-%d").date()
        elif len(parts) == 2:
            date = datetime(today.year, int(parts[0]), int(parts[1])).date()
        else:
            raise ValueError("Invalid format")

        await state.update_data(date=date.strftime("%Y-%m-%d"))
        data = await state.get_data()
        timestamp = int(datetime.now().timestamp())
        jadval_db.add_jadval(data['title'], data['date'], data['start_time'], data['end_time'], timestamp)

        await message.answer(
            f"✅ {data['title']} jadvali {data['date']} kuni {data['start_time']} - {data['end_time']} ga qo‘shildi!",reply_markup=orqa_inline
        )
        await state.finish()
    except ValueError:
        await message.answer("⚠️ Iltimos, sanani YYYY-MM-DD yoki MM-DD formatida kiriting!")


@dp.callback_query_handler(lambda c: c.data == 'dars_ochirish')
async def dars_ochirish(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("❌ Darsni o‘chirish uchun ID-ni kiriting:")

@dp.message_handler(lambda message: message.text.isdigit())
async def delete_jadval(message: types.Message):
    jadval_id = int(message.text)
    jadval_db.delete_jadval(jadval_id)
    await message.answer(f"✅ Jadval ID-{jadval_id} o‘chirildi!",reply_markup=orqa_inline)

@dp.callback_query_handler(lambda c: c.data == 'jadvallimi')
async def show_upcoming_lessons(call: CallbackQuery):
    await call.message.delete()
    lessons = jadval_db.get_upcoming_lessons()
    if not lessons:
        await call.message.answer("📭 Kelgusi darslar mavjud emas!",reply_markup=orqasi_inline)
        return

    text = "📅 <b>Kelgusi darslar:</b>\n"
    for lesson in lessons:
        text += (f"\n📌 <b>{lesson[1]}</b>\n"
                 f"📅 <b>Sana:</b> {lesson[2]}\n"
                 f"⏳ <b>Boshlanish:</b> {lesson[3]}\n"
                 f"⏰ <b>Tugash:</b> {lesson[4]}\n")
    await call.message.answer(text,reply_markup=orqasi_inline)

@dp.callback_query_handler(lambda c: c.data == 'otgan_dars')
async def show_past_lessons(call: CallbackQuery):
    await call.message.delete()
    lessons = jadval_db.get_past_lessons()
    if not lessons:
        await call.message.answer("📭 O‘tgan darslar mavjud emas!",reply_markup=orqasi_inline)
        return

    text = "📅 <b>O‘tgan darslar:</b>\n"
    for lesson in lessons:
        text += (f"\n📌 <b>{lesson[1]}</b>\n"
                 f"📅 <b>Sana:</b> {lesson[2]}\n"
                 f"⏳ <b>Boshlanish:</b> {lesson[3]}\n"
                 f"⏰ <b>Tugash:</b> {lesson[4]}\n")
    await call.message.answer(text,reply_markup=orqasi_inline)


@dp.callback_query_handler(text=['jadval_yangilash'])
async def update_jadval_start(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("🔄 Yangilamoqchi bo‘lgan darsning ID raqamini kiriting:")
    await UpdateJadval.id.set()


@dp.message_handler(state=UpdateJadval.id)
async def set_update_id(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(id=int(message.text))
        await message.answer("📝 Yangi sarlavhani kiriting:")
        await UpdateJadval.next()
    else:
        await message.answer("⚠️ Iltimos, faqat raqam kiriting!",reply_markup=orqa_inline)
        await state.finish()

@dp.message_handler(state=UpdateJadval.title)
async def set_update_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📅 Yangi dars sanasini kiriting (YYYY-MM-DD yoki MM-DD formatda):")
    await UpdateJadval.next()

@dp.message_handler(state=UpdateJadval.date)
async def set_update_date(message: types.Message, state: FSMContext):
    try:
        today = datetime.today()
        parts = message.text.split("-")

        if len(parts) == 3:
            date = datetime.strptime(message.text, "%Y-%m-%d").date()
        elif len(parts) == 2:
            date = datetime(today.year, int(parts[0]), int(parts[1])).date()
        else:
            raise ValueError("Invalid format")

        await state.update_data(date=date.strftime("%Y-%m-%d"))
        await message.answer("⏳ Yangi boshlanish vaqtini kiriting (HH:MM formatda):")
        await UpdateJadval.next()
    except ValueError:
        await message.answer("⚠️ Iltimos, sanani YYYY-MM-DD yoki MM-DD formatida kiriting!")

@dp.message_handler(state=UpdateJadval.start_time)
async def set_update_start_time(message: types.Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%H:%M")
        await state.update_data(start_time=message.text)
        await message.answer("⏰ Yangi tugash vaqtini kiriting (HH:MM formatda):")
        await UpdateJadval.next()
    except ValueError:
        await message.answer("⚠️ Iltimos, vaqtni HH:MM formatida kiriting!")

@dp.message_handler(state=UpdateJadval.end_time)
async def set_update_end_time(message: types.Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%H:%M")
        await state.update_data(end_time=message.text)
        data = await state.get_data()

        # Ma'lumotlarni yangilash
        jadval_db.update_jadval(
            jadval_id=data['id'],
            title=data['title'],
            date=data['date'],
            start_time=data['start_time'],
            end_time=data['end_time']
        )

        await message.answer(f"✅ Dars ID: {data['id']} yangilandi!\n"
                             f"📅 Sana: {data['date']}\n"
                             f"⏳ Vaqt: {data['start_time']} - {data['end_time']}\n"
                             f"📌 Sarlavha: {data['title']}",reply_markup=orqa_inline)
        await state.finish()
    except ValueError:
        await message.answer("⚠️ Iltimos, vaqtni HH:MM formatida kiriting!",reply_markup=orqa_inline)
        await state.finish()


#---------------XABAR---------------------
@dp.callback_query_handler(text='xabar')
async def list_students_handler(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("barch",reply_markup=xabar_inline)

@dp.callback_query_handler(text='malum_oquvchiga_xabar')
async def list_students_handler(call: CallbackQuery):
    await call.message.delete()
    students = user_db.get_all_students()  # Barcha studentlarni olish

    if not students:
        await call.message.answer("Hozircha hech qanday student yo'q.",reply_markup=orqa_inline)
        return

    keyboard = InlineKeyboardMarkup()
    for student in students:
        student_id = student[0]
        full_name = student[1]   

        button = InlineKeyboardButton(text=full_name, callback_data=f"send_student_{student_id}")
        keyboard.add(button)

    await call.message.answer("Xabar yubormoqchi bo'lgan studentni tanlang:", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith("send_student_"))
async def send_message_to_student(callback_query: CallbackQuery, state: FSMContext):
    telegram_id = int(callback_query.data.replace("send_student_", ""))
    await bot.send_message(callback_query.from_user.id, "Iltimos, yubormoqchi bo'lgan xabaringizni kiriting:")
    await state.update_data(telegram_id=telegram_id)
    await SendMessageState.waiting_for_message.set()

@dp.message_handler(state=SendMessageState.waiting_for_message, content_types=types.ContentTypes.TEXT)
async def get_user_message(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    telegram_id = user_data.get("telegram_id")

    try:
        await user_db.send_message_to_user(telegram_id, message.text)
        await message.answer("Xabar muvaffaqiyatli yuborildi! ✅",reply_markup=orqa_inline)
        await state.finish()
    except Exception as e:
        await message.answer(f"Xabar muvoffiqiyatli yuborildi!",reply_markup=orqa_inline)
        await state.finish()

    await state.finish()

@dp.callback_query_handler(text='guruxga_xabar')
async def list_groups_handler(call: CallbackQuery):
    await call.message.delete()
    groups = user_db.get_all_groups()

    if not groups:
        await call.message.answer("Hozircha hech qanday guruh yo'q.")
        return

    keyboard = InlineKeyboardMarkup()
    for group in groups:
        group_id = group[0]
        group_name = group[1] if len(group) > 1 and group[1] else f"Guruh {group_id}"
        button = InlineKeyboardButton(text=group_name, callback_data=f"send_group_{group_id}")
        keyboard.add(button)

    await call.message.answer("Xabar yubormoqchi bo'lgan guruhni tanlang:", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith("send_group_"))
async def send_message_to_group(callback_query: CallbackQuery, state: FSMContext):
    group_id = callback_query.data.replace("send_group_", "")
    await bot.send_message(callback_query.from_user.id, "Iltimos, yubormoqchi bo'lgan xabaringizni kiriting:")
    await state.update_data(group_id=group_id)
    await SendMessageState.waiting_for_group_message.set()

@dp.message_handler(state=SendMessageState.waiting_for_group_message, content_types=types.ContentTypes.TEXT)
async def get_group_message(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    group_id = user_data.get("group_id")

    try:
        await user_db.send_message_to_group(group_id, message.text)
        await message.answer("✅ Xabar guruhdagi barcha studentlarga yuborildi!",reply_markup=orqa_inline)
        await state.finish()
    except Exception as e:
        await message.answer(f"❌ Xabar yuborishda xatolik",reply_markup=orqa_inline)
        await state.finish()

    await state.finish()

@dp.callback_query_handler(text='umumiy_xabar')
async def send_all_handler(call:CallbackQuery):
    await call.message.delete()
    await call.message.answer("📩 Iltimos, yubormoqchi bo‘lgan xabaringizni kiriting:")
    await SendMessageState.waiting_for_all_message.set()

@dp.message_handler(state=SendMessageState.waiting_for_all_message, content_types=types.ContentTypes.TEXT)
async def get_all_message(message: types.Message, state: FSMContext):
    try:
        await user_db.send_message_to_all(message.text)
        await message.answer("✅ Xabar barcha foydalanuvchilarga yuborildi!",reply_markup=orqa_inline)
    except Exception as e:
        await message.answer(f"✅Xabar barcha foydalanuvchiga yuborildi",reply_markup=orqa_inline)

    await state.finish()

@dp.callback_query_handler(text='yuboril_xabar')
async def view_messages_handler(call:CallbackQuery):
    await call.message.delete()
    messages = user_db.get_last_messages(10)
    if not messages:
        await call.message.answer("📭 Hali hech qanday xabar yuborilmagan.",reply_markup=orqa_inline)
        return

    response = "📩 *Oxirgi yuborilgan xabarlar:*\n\n"
    for msg in messages:
        response += f"👤 *Foydalanuvchi:* {msg[0]}\n📜 *Xabar:* {msg[2]}\n🕰 *Vaqt:* {msg[3]}\n"
        response += "———————————————\n"

    await call.message.answer(response,reply_markup=orqa_inline)




#-----------------Sozlama---------------------------------------
# ✅ Sozlamalar menyusi
@dp.callback_query_handler(text='sozlama')
async def list_students_handler(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("⚙️ Sozlamalar menyusi:", reply_markup=sozlama_inline)


# ✅ Admin qo‘shish
@dp.callback_query_handler(text="admin_qosh")
async def add_admin_handler(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("👤 Yangi admin qo‘shish uchun, Telegram ID va ismini kiriting:\n\n"
                              "📝 *Misol:* `123456789 Ism Familiya`", parse_mode="MarkdownV2")

    # Holatga foydalanuvchi ID'sini saqlaymiz
    await state.update_data(admin_requester=call.from_user.id)
    await AdminStates.admin.set()


@dp.message_handler(state=AdminStates.admin)
async def process_admin_add(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    # Faqat "admin_qosh" tugmasi bosgan foydalanuvchi foydalanishi mumkin
    if message.from_user.id != user_data.get("admin_requester"):
        return

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("❌ Foydalanish tartibi:\n`123456789 Ism Familiya`", parse_mode="MarkdownV2")
        await state.finish()
        return

    try:
        telegram_id = int(args[0])
        full_name = args[1]

        admin_db.add_admin(telegram_id, full_name)

        await message.answer(f"✅ *{full_name}* \n\n(*ID:* `{telegram_id}`\n\n) admin sifatida qo‘shildi\\!",reply_markup=orqa_inline)
    except ValueError:
        await message.answer("❌ Xatolik: Telegram ID faqat raqam bo‘lishi kerak!",reply_markup=orqa_inline)
        await state.finish()

    # Holatni tugatamiz
    await state.finish()


# ✅ Adminlar ro‘yxati
@dp.callback_query_handler(text="admin_roxati")
async def list_admins_handler(call: CallbackQuery):
    await call.message.delete()
    admins = admin_db.get_all_admins()

    if not admins:
        await call.message.answer("❌ Hali hech qanday admin yo‘q.",reply_markup=orqa_inline)
        return

    response = "👮‍♂️ *Adminlar ro‘yxati:*\n\n"
    for admin in admins:
        response += f"🆔 `{admin[0]}` - *{admin[1]}*\n-------------------------------\n"

    await call.message.answer(response,reply_markup=orqa_inline)


# ✅ Adminni o‘chirish tugmalari
@dp.callback_query_handler(text="adminni_och")
async def remove_admin_handler(call: CallbackQuery):
    await call.message.delete()
    admins = admin_db.get_all_admins()

    if not admins:
        await call.message.answer("❌ Hozircha hech qanday admin yo‘q.",reply_markup=orqa_inline)
        return

    # 🎯 Inline tugmalar yaratish
    keyboard = InlineKeyboardMarkup(row_width=1)  # Har bir qator uchun 1 ta tugma
    for admin in admins:
        admin_id = admin[0]
        admin_name = admin[1] if len(admin) > 1 else f"Admin {admin_id}"  # Ism yoki ID

        button = InlineKeyboardButton(
            text=admin_name,
            callback_data=f"confirm_remove_admin:{admin_id}"
        )
        keyboard.add(button)

    await call.message.answer(
        "🛑 O‘chirmoqchi bo‘lgan adminni tanlang:",
        reply_markup=keyboard
    )


# ✅ Adminni o‘chirishni tasdiqlash
@dp.callback_query_handler(lambda c: c.data.startswith("confirm_remove_admin:"))
async def confirm_remove_admin(callback_query: CallbackQuery):
    telegram_id = int(callback_query.data.split(":")[1])

    # 🔍 Admin mavjudligini tekshirish
    if not admin_db.is_admin_exists(telegram_id):
        await callback_query.message.answer(
            f"❌ Xatolik: `{telegram_id}` ID ga ega admin topilmadi!",
            parse_mode="Markdown"
        )
        return

    # 🗑 Adminni bazadan o‘chirish
    admin_db.delete_admin(telegram_id)

    await callback_query.message.answer(
        f"✅ Admin (*ID:* `{telegram_id}`) o‘chirildi!",reply_markup=orqa_inline
    )

@dp.callback_query_handler(lambda c: c.data == "admin_static")
async def admin_statistics_handler(call: CallbackQuery):
    await call.message.delete()
    stats = admin_db.get_statistics()

    text = (
        "📊 <b>Statistika:</b>\n\n"
        f"👨‍💼 <b>Adminlar soni:</b> {stats['admins']}\n"
        f"👥 <b>Foydalanuvchilar soni:</b> {stats['users']}\n"
    )

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔙 Ortga", callback_data="orqaga")
    )

    await call.message.answer(text, reply_markup=keyboard)


#----------------Orqa------------------------

@dp.callback_query_handler(text='orqaga')
async def bosh_malumotlar(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Barcha ma'lumotlar!", reply_markup=admin_inline)



#-------------------status----------------------
@dp.message_handler(commands=["barcha_oquvchilar"])
async def show_students(message: Message):
    students = user_db.get_all_students()  # (id, fullname) formatida qaytishi kerak
    if not students:
        await message.answer("Hozircha ro'yxatda o'quvchilar yo'q.")
        return

    keyboard = InlineKeyboardMarkup(row_width=2)
    for student in students[:10]:  # Faqat 10tasini chiqaramiz
        keyboard.add(InlineKeyboardButton(text=student[1], callback_data=f"select_student:{student[0]}"))

    await message.answer("O'quvchini tanlang:", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("select_student:"))
async def ask_status_change(call: CallbackQuery):
    student_id = call.data.split(":")[1]

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="Faol", callback_data=f"change_status:{student_id}:faol"),
        InlineKeyboardButton(text="Faolsiz", callback_data=f"change_status:{student_id}:faolsiz")
    )

    await call.message.edit_text("O'quvchining statusini tanlang:", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("change_status:"))
async def update_student_status(call: CallbackQuery):
    _, student_id, new_status = call.data.split(":")  # ID va yangi statusni ajratamiz

    try:
        user_db.update_student_status(student_id, new_status)
        await call.message.edit_text(f"✅ O‘quvchi statusi muvaffaqiyatli o‘zgartirildi: <b>{new_status}</b>")
    except ValueError as e:
        await call.answer(str(e), show_alert=True)



@dp.message_handler(commands=["faollar"])
async def show_active_students(message: Message):
    students = user_db.get_students_by_status("faol")  # Faqat faol o'quvchilarni olish

    if not students:
        await message.answer("Hozircha faol o'quvchilar yo'q.")
        return

    keyboard = InlineKeyboardMarkup(row_width=2)
    for student in students:
        keyboard.add(InlineKeyboardButton(text=student[1], callback_data=f"student_info:{student[0]}"))

    await message.answer("Faol o'quvchilar:", reply_markup=keyboard)


@dp.message_handler(commands=["faolsizlar"])
async def show_inactive_students(message: Message):
    students = user_db.get_students_by_status("faolsiz")  # Faqat faolsiz o'quvchilarni olish

    if not students:
        await message.answer("Hozircha faolsiz o'quvchilar yo'q.")
        return

    keyboard = InlineKeyboardMarkup(row_width=2)
    for student in students:
        keyboard.add(InlineKeyboardButton(text=student[1], callback_data=f"student_info:{student[0]}"))

    await message.answer("Faolsiz o'quvchilar:", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith("student_info:"))
async def show_student_info(call: CallbackQuery):
    student_id = call.data.split(":")[1]
    student = user_db.get_student_by_id(student_id)  # ID bo‘yicha o‘quvchini olish

    if not student:
        await call.answer("Bunday o'quvchi topilmadi.", show_alert=True)
        return

    full_name = student[1]
    status = student[2]  # Status faqat "faol" yoki "faolsiz" bo'ladi
    group_id = student[3]

    await call.message.answer(f"👤 O'quvchi: {full_name}\n📌Gruh: {group_id} \n📌 Status: {status} \n")



@dp.message_handler()
async def update_activity(message: Message):
    user_db.update_last_active(message.from_user.id)


