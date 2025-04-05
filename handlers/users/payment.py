from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import asyncio
from keyboards.inline.admin import tolov_inline, orqa_inline
from states.states import PaymentStates,PaymentAmountState
from loader import dp, bot, admin_db, user_db
from loader import pyment_db



@dp.callback_query_handler(text='tolov')
async def oqtuvchi_malumotlar(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Barcha ma'lumotlar!", reply_markup=tolov_inline)


# ✅ To‘lov qilish tugmasi
@dp.callback_query_handler(text="tolov_q")
async def payment_request(call: CallbackQuery):
    telegram_id = call.message.from_user.id

    # Talaba "faol" bo‘lmasa, unga xabar yuborish
    if not pyment_db.is_student_active(telegram_id):
        await call.message.answer("📢 Siz to`lov qilmagansiz! Iltimos, to`lovni amalga oshiring.")

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("💳 To‘lov qilish", callback_data="pay_now")
    )
    await call.message.answer("📢 To‘lov vaqtingiz keldi. Iltimos, to‘lovni amalga oshiring!", reply_markup=keyboard)

# ✅ Karta raqami yuborish
@dp.callback_query_handler(lambda call: call.data == "pay_now")
async def send_payment_details(call: CallbackQuery):
    await call.message.answer("💳 To‘lov uchun karta raqami: 8600 1234 5678 9101\n\n✅ To‘lov qilganingizdan keyin chekni yuboring.")

# ✅ To‘lov chekini qabul qilish
@dp.message_handler(content_types=types.ContentType.PHOTO, state=None)
async def handle_payment_receipt(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    file_id = message.photo[-1].file_id

    # ✅ To‘lov chekini bazaga vaqtincha saqlash
    await state.update_data(file_id=file_id)
    await state.update_data(telegram_id=telegram_id)

    await message.answer("💰 Nechpul yubordingiz? Iltimos, summani faqat raqamlarda kiriting.")
    await PaymentAmountState.waiting_for_amount.set()  # Keyingi bosqichga o‘tish

# ✅ To‘lov summasini qabul qilish
@dp.message_handler(state=PaymentAmountState.waiting_for_amount)
async def process_payment_amount(message: types.Message, state: FSMContext):
    amount = message.text.strip()

    if not amount.isdigit():
        await message.answer("❌ Xatolik! To‘lov summasini faqat raqamda kiriting.")
        return

    amount = float(amount)  # Summani float shakliga o'tkazamiz
    payment_date = datetime.now().strftime("%Y-%m-%d")  # Hozirgi sana

    data = await state.get_data()
    telegram_id = data["telegram_id"]
    file_id = data["file_id"]

    # ✅ To‘lovni bazaga saqlash
    pyment_db.add_payment(telegram_id, amount, payment_date)

    await message.answer(f"✅ Sizning {amount} so‘m to‘lovingiz qabul qilindi. Admin tekshiradi.")

    # ✅ Adminlarga yuborish
    user_info = user_db.get_user_info(telegram_id)
    if user_info:
        full_name = user_info['full_name']
        group = user_info['group_id']
    else:
        full_name = "Ism topilmadi"
        group = "Guruh topilmadi"

    admin_ids = admin_db.get_admin_ids()
    if admin_ids:
        keyboard = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirma_{telegram_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{telegram_id}")
        )

        for admin_id in admin_ids:
            caption = (
                f"📝 *Yangi to‘lov!*\n"
                f"👤 *Foydalanuvchi:* {full_name}\n"
                f"🎓 *Guruh:* {group}\n"
                f"💰 *Summasi:* {amount} so‘m\n"
                f"🆔 *Telegram ID:* {telegram_id}\n"
                f"📅 *Sana:* {payment_date}"
            )

            await bot.send_photo(admin_id, file_id, caption=caption, parse_mode="Markdown", reply_markup=keyboard)

    await state.finish()  # Holatni tugatamiz

@dp.callback_query_handler(lambda c: c.data.startswith("confirma_"))
async def confirm_payment(callback_query: CallbackQuery):
    telegram_id = int(callback_query.data.split("_")[1])

    # 🔄 Foydalanuvchi statusini "active" qilish
    user_db.update_user_status(telegram_id, "faol")

    await bot.answer_callback_query(callback_query.id, "✅ To‘lov tasdiqlandi!")
    await bot.send_message(telegram_id, "✅ Sizning to‘lovingiz tasdiqlandi. Kursdan foydalanishingiz mumkin!")

# ❌ To‘lovni rad etish
@dp.callback_query_handler(lambda c: c.data.startswith("reject_"))
async def reject_payment(callback_query: CallbackQuery):
    telegram_id = int(callback_query.data.split("_")[1])

    # 🔄 Foydalanuvchi statusini "inactive" qilish
    user_db.update_user_status(telegram_id, "faolsiz")

    await bot.answer_callback_query(callback_query.id, "❌ To‘lov rad etildi!")
    await bot.send_message(telegram_id, "❌ Sizning to‘lovingiz rad etildi. Iltimos, administrator bilan bog‘laning.")

# ✅ Foydalanuvchi to‘lov tarixini ko‘rishi
@dp.callback_query_handler(text=['tolov_t'])
async def show_my_payments(call:CallbackQuery):
    telegram_id = call.from_user.id
    payments = pyment_db.get_payments_by_user(telegram_id)

    if not payments:
        await call.message.answer("❌ Sizda hech qanday to‘lov mavjud emas.")
        return

    text = "📜 *Sizning to‘lovlaringiz:*\n\n"
    for payment in payments:
        amount, status, created_at = payment
        text += f"📅 *Sana:* {created_at}\n"
        text += f"📌 *Holat:* {status}\n"
        text += "--------------------------\n"

    await call.message.answer(text, parse_mode="Markdown")




@dp.callback_query_handler(text="tolov_tarixi")
async def list_paid_users(call:CallbackQuery):
    paid_users = pyment_db.get_all_payments()  # To‘lov qilgan foydalanuvchilar ro‘yxati

    if not paid_users:
        await call.message.answer("📢 Hali hech kim to‘lov qilmagan.")
        return

    text = "✅ To‘lov qilgan foydalanuvchilar:\n"
    for user in paid_users:
        telegram_id = user[0]  # tuple-da birinchi element - telegram_id
        payment_date = user[1]  # tuple-da ikkinchi element - to‘lov sanasi

        # ✅ Foydalanuvchi ismini `user_db` dan olish
        user_info = user_db.get_user_info(telegram_id)
        full_name = user_info["full_name"] if user_info else "Ism topilmadi"
        group_id=user_info["group_id"]

        text += f"👤 {full_name}\n👥 {group_id}\n📅 {payment_date}\n\n-------------------\n\n"

    await call.message.answer(text)

@dp.message_handler(commands=["delete_payment"])
async def show_paid_users(message: types.Message):
    paid_users = pyment_db.get_all_payments()  # To‘lov qilgan foydalanuvchilar ro‘yxati

    if not paid_users:
        await message.answer("📢 Hali hech kim to‘lov qilmagan.")
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for user in paid_users:
        telegram_id = user[0]
        payment_date = user[1]

        # ✅ Foydalanuvchi ismini `user_db` dan olish
        user_info = user_db.get_user_info(telegram_id)
        full_name = user_info["full_name"] if user_info else "Ism topilmadi"

        button_text = f"🗑 {full_name} - {payment_date}"
        keyboard.add(InlineKeyboardButton(button_text, callback_data=f"delete_{telegram_id}"))

    await message.answer("🗑 O‘chirmoqchi bo‘lgan foydalanuvchini tanlang:", reply_markup=keyboard)



@dp.callback_query_handler(lambda call: call.data.startswith("delete_"))
async def delete_selected_payment(call: CallbackQuery):
    telegram_id = int(call.data.split("_")[1])  # Callback data dan ID olish

    if pyment_db.delete_payment(telegram_id):
        await call.message.edit_text(f"✅ {telegram_id} foydalanuvchining to‘lov ma’lumotlari o‘chirildi.")
    else:
        await call.message.edit_text(f"⚠️ {telegram_id} foydalanuvchining to‘lov ma’lumotlari topilmadi!")


@dp.callback_query_handler(text="tolov_holati")
async def show_active_users(call:CallbackQuery):
    await call.message.delete()
    active_users = user_db.get_active_users()  # Faqat "faol" foydalanuvchilarni olish

    if not active_users:
        await call.message.answer("📢 Hozirda hech kim qarzdorlar yo`q.",reply_markup=orqa_inline)
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for user in active_users:
        telegram_id = user[0]
        full_name = user[1]
        group_id=user[2]
        phone=user[3]


        await call.message.answer(f"✅ Qarzdorligi yo`q foydalanuvchilar ro‘yxati:\n\n 🪪Ism-Familya: {full_name}\n 👥Gruh nomi: {group_id}\n 📞Tel: {phone}\n-------------------",reply_markup=orqa_inline)


@dp.callback_query_handler(text="qarzni_korish")
async def show_inactive_users(call:CallbackQuery):
    await call.message.delete()
    inactive_users = user_db.get_inactive_users()  # Faqat "faolsiz" foydalanuvchilarni olish

    if not inactive_users:
        await call.message.answer("📢 Hozirda barcha foydalanuvchilar qarzi yo`q!",reply_markup=orqa_inline)
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for user in inactive_users:
        telegram_id = user[0]
        full_name = user[1]
        group_id= user[2]
        phone= user[3]

        await call.message.answer(f"🚫 Qarzdor foydalanuvchilar ro‘yxati:\n\n 🪪Ism-Familya: {full_name}\n 👥Gruh nomi: {group_id}\n 📞Tel: {phone}\n-------------------",reply_markup=orqa_inline)


# ✅ 1️⃣ O‘quvchi ismini kiritish
@dp.callback_query_handler(text="tolov_qoshish")
async def start_payment_process(call:CallbackQuery):
    await call.message.delete()
    await call.message.answer("📌 To‘lov qo‘shish uchun o‘quvchining *to‘liq ismini* kiriting:")
    await PaymentStates.waiting_for_full_name.set()

# ✅ 2️⃣ Guruh ID ni kiritish
@dp.message_handler(state=PaymentStates.waiting_for_full_name)
async def enter_group_id(message: types.Message, state: FSMContext):
    full_name = message.text.strip()

    # O‘quvchini bazadan qidirish
    students = user_db.get_students_by_name(full_name)

    if not students:
        await message.answer("🚫 Bunday ismli o‘quvchi topilmadi! Iltimos, qayta tekshirib kiriting.")
        return

    await state.update_data(full_name=full_name)
    await message.answer(f"🎓 {full_name} uchun guruh ID ni kiriting:")
    await PaymentStates.waiting_for_group_id.set()

@dp.message_handler(state=PaymentStates.waiting_for_group_id)
async def enter_payment_amount(message: types.Message, state: FSMContext):
    group_id = message.text.strip()

    if not group_id:
        await message.answer("❌ Iltimos, guruh nomini kiriting!")
        await state.finish()
        return

    # Oldingi bosqichdagi ma'lumotlarni olish
    data = await state.get_data()
    full_name = data["full_name"]

    # O‘quvchini bazadan qidirish
    student = user_db.get_student_by_name_and_groups(full_name, group_id)

    if not student:
        await message.answer(f"🚫 *{full_name}* ushbu guruh ({group_id})da topilmadi!\nIltimos, qayta tekshirib kiriting.", parse_mode="Markdown")
        return

    # O‘quvchi ID sini olish
    student_id = student["telegram_id"]  # Bu yerda TypeError bo‘lmasligi uchun dict qaytishi kerak!

    # O‘quvchi ma’lumotlarini saqlash
    await state.update_data(group_id=group_id, student_id=student_id)

    await message.answer(f"💰 *{full_name} ({group_id})* uchun to‘lov summasini kiriting:", parse_mode="Markdown")
    await PaymentStates.waiting_for_amount.set()

# ✅ 4️⃣ To‘lov sanasini kiritish
@dp.message_handler(state=PaymentStates.waiting_for_amount)
async def enter_payment_date(message: types.Message, state: FSMContext):
    amount = message.text.strip()

    if not amount.isdigit():
        await message.answer("❌ Iltimos, to‘lov summasini faqat raqamda kiriting!")
        return

    await state.update_data(amount=float(amount))
    await message.answer("📅 To‘lov sanasini `YYYY-MM-DD` formatida kiriting:")
    await PaymentStates.waiting_for_date.set()

# ✅ 5️⃣ To‘lovni tasdiqlash va o‘quvchiga xabar yuborish
@dp.message_handler(state=PaymentStates.waiting_for_date)
async def confirm_payment(message: types.Message, state: FSMContext):
    payment_date = message.text.strip()

    try:
        datetime.strptime(payment_date, "%Y-%m-%d")  # Sana formatini tekshirish
    except ValueError:
        await message.answer("❌ Xato! Sanani `YYYY-MM-DD` formatida kiriting!")
        return

    data = await state.get_data()
    student_id = data["student_id"]
    full_name = data["full_name"]
    group_id = data["group_id"]
    amount = data["amount"]

    if pyment_db.add_payment(student_id, amount,payment_date):
        await message.answer(
            f"✅ *Yangi to‘lov qo‘shildi!*\n\n"
            f"👤 *O‘quvchi:* {full_name}\n"
            f"🎓 *Guruh:* {group_id}\n"
            f"💰 *Summasi:* {amount} so`m\n"
            f"📅 *Sana:* {payment_date}",
            reply_markup=orqa_inline
        )

        # ✅ O‘quvchiga yangi to‘lov haqida xabar yuborish
        try:
            await bot.send_message(student_id, f"📢 Sizga yangi to‘lov qo‘shildi:\n\n"
                                               f"💰 Summa: {amount} so`m\n"
                                               f"📅 Sana: {payment_date}")
        except:
            await message.answer(f"⚠️ {full_name} ({group_id}) ga xabar yuborilmadi! (Bot foydalanuvchini bloklagan bo‘lishi mumkin)")

    else:
        await message.answer("❌ Xatolik! To‘lov qo‘shilmadi.")

    await state.finish()


@dp.message_handler(commands=["my_admin_payments"])
async def show_admin_payments(message: types.Message):
    telegram_id = message.from_user.id
    payments = pyment_db.get_admin_added_payments_by_telegram_id(telegram_id)

    if not payments:
        await message.answer("❌ Siz uchun hali admin tomonidan hech qanday to‘lov qo‘shilmagan.")
        return

    text = "✅ *Admin tomonidan qo‘shilgan to‘lovlar:* \n\n"
    for payment in payments:
        text += f"📅 *Sana:* {payment['payment_date']}\n💰 *Summasi:* {payment['amount']}$\n👤 *Admin ID:* {payment['admin_id']}\n\n"

    await message.answer(text, parse_mode="Markdown")




async def send_payment_reminders():
    """
    Har 24 soatda to‘lov muddati o‘tgan talabalarga eslatma yuborish va holatni yangilash.
    """
    while True:
        # To‘lov muddati o‘tgan talabalarni olish
        due_students = pyment_db.get_due_payments()

        for student in due_students:
            telegram_id = student["telegram_id"]
            last_payment_date = student["created_at"]
            user_status = user_db.get_user_status(telegram_id)

            # Joriy vaqt bilan oxirgi to‘lov sanasi orasidagi farqni hisoblash
            import datetime
            days_since_payment = (datetime.datetime.now() - last_payment_date).days

            # Agar 30 kundan oshgan bo‘lsa
            if days_since_payment >= 30:
                if user_status == "faolsiz":
                    # Faolsiz talabalarga eslatma yuborish
                    await bot.send_message(
                        telegram_id,
                        "📢 Hurmatli talaba, sizning to‘lovingiz muddati tugagan. Iltimos, to‘lovni amalga oshiring!"
                    )
                elif user_status == "faol":
                    # Faol talabalarni faolsizga o‘tkazish
                    user_db.update_user_status(telegram_id, "faolsiz")

        # 24 soat (86400 soniya) kutish
        await asyncio.sleep(86400)
