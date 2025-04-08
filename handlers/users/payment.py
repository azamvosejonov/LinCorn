import asyncio
import logging
from datetime import timedelta

from aiogram.types import CallbackQuery

from keyboards.inline.user import tolovlar_inline, orqasi_inline
from loader import dp, bot, admin_db, user_db
from loader import pyment_db
from states.states import PaymentStates, PaymentAmountState


@dp.callback_query_handler(text='mening_tol')
async def oqtuvchi_malumotlar(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Barcha ma'lumotlar!", reply_markup=tolovlar_inline)


# ✅ To‘lov qilish tugmasi
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime




# To‘lov so‘rovi
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


# Karta raqami yuborish
@dp.callback_query_handler(lambda call: call.data == "pay_now")
async def send_payment_details(call: CallbackQuery):
    await call.message.answer(
        "💳 To‘lov uchun karta raqami: 8600 1234 5678 9101\n\n✅ To‘lov qilganingizdan keyin chekni yuboring.")


# To‘lov chekini qabul qilish
@dp.message_handler(content_types=types.ContentType.PHOTO, state=None)
async def handle_payment_receipt(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    file_id = message.photo[-1].file_id

    # To‘lov chekini bazaga vaqtincha saqlash
    await state.update_data(file_id=file_id)
    await state.update_data(telegram_id=telegram_id)

    await message.answer("💰 Nechpul yubordingiz? Iltimos, summani faqat raqamlarda kiriting.")
    await PaymentAmountState.waiting_for_amount.set()


# To‘lov summasini qabul qilish
@dp.message_handler(state=PaymentAmountState.waiting_for_amount)
async def process_payment_amount(message: types.Message, state: FSMContext):
    amount = message.text.strip()

    if not amount.isdigit():
        await message.answer("❌ Xatolik! To‘lov summasini faqat raqamda kiriting.")
        return

    amount = float(amount)
    payment_date = datetime.now().strftime("%Y-%m-%d")

    data = await state.get_data()
    telegram_id = data["telegram_id"]
    file_id = data["file_id"]

    # To‘lovni bazaga saqlash
    pyment_db.add_payment(telegram_id, amount, payment_date)

    await message.answer(f"✅ Sizning {amount} so‘m to‘lovingiz qabul qilindi. Admin tekshiradi.")

    # Adminlarga yuborish
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

    await state.finish()


# To‘lovni tasdiqlash
@dp.callback_query_handler(lambda c: c.data.startswith("confirma_"))
async def confirm_payment(callback_query: CallbackQuery):
    telegram_id = int(callback_query.data.split("_")[1])

    # Foydalanuvchi statusini "faol" qilish
    user_db.update_user_status(telegram_id, "faol")

    # Payments jadvalida to‘lovni tasdiqlash
    pyment_db.confirm_payment(telegram_id)

    await bot.answer_callback_query(callback_query.id, "✅ To‘lov tasdiqlandi!")
    await bot.send_message(telegram_id, "✅ Sizning to‘lovingiz tasdiqlandi. Kursdan foydalanishingiz mumkin!")


# To‘lovni rad etish (qo'shimcha funksiya)
@dp.callback_query_handler(lambda c: c.data.startswith("reject_"))
async def reject_payment(callback_query: CallbackQuery):
    telegram_id = int(callback_query.data.split("_")[1])

    await bot.answer_callback_query(callback_query.id, "❌ To‘lov rad etildi!")
    await bot.send_message(telegram_id, "❌ Sizning to‘lovingiz rad etildi. Iltimos, qayta urinib ko‘ring.")
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
        await call.message.answer("📢 Hozirda hech kim qarzdorlar yo`q.",reply_markup=orqasi_inline)
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for user in active_users:
        telegram_id = user[0]
        full_name = user[1]
        group_id=user[2]
        phone=user[3]


        await call.message.answer(f"✅ Qarzdorligi yo`q foydalanuvchilar ro‘yxati:\n\n 🪪Ism-Familya: {full_name}\n 👥Gruh nomi: {group_id}\n 📞Tel: {phone}\n-------------------",reply_markup=orqasi_inline)


@dp.callback_query_handler(text="qarzni_korish")
async def show_inactive_users(call:CallbackQuery):
    await call.message.delete()
    inactive_users = user_db.get_inactive_users()  # Faqat "faolsiz" foydalanuvchilarni olish

    if not inactive_users:
        await call.message.answer("📢 Hozirda barcha foydalanuvchilar qarzi yo`q!",reply_markup=orqasi_inline)
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for user in inactive_users:
        telegram_id = user[0]
        full_name = user[1]
        group_id= user[2]
        phone= user[3]

        await call.message.answer(f"🚫 Qarzdor foydalanuvchilar ro‘yxati:\n\n 🪪Ism-Familya: {full_name}\n 👥Gruh nomi: {group_id}\n 📞Tel: {phone}\n-------------------",reply_markup=orqasi_inline)


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
    """
    Handles payment date confirmation and processes the payment addition.

    Args:
        message: Telegram message object containing the date
        state: FSMContext for managing conversation state
    """
    payment_date = message.text.strip()

    # Validate date format
    try:
        datetime.strptime(payment_date, "%Y-%m-%d")
    except ValueError:
        await message.answer(
            "❌ Xato! Iltimos, sanani to‘g‘ri formatda kiriting: `YYYY-MM-DD`\n"
            "Masalan: 2025-04-06"
        )
        return

    # Get stored data from state
    try:
        data = await state.get_data()
        student_id = data.get("student_id")
        full_name = data.get("full_name")
        group_id = data.get("group_id")
        amount = data.get("amount")

        # Verify all required data is present
        if not all([student_id, full_name, group_id, amount]):
            await message.answer("❌ Xatolik! To‘lov ma’lumotlari to‘liq emas.")
            await state.finish()
            return

        # Add payment to database
        if pyment_db.add_payment(student_id, amount, payment_date):
            # Format success message
            success_message = (
                "✅ *Yangi to‘lov muvaffaqiyatli qo‘shildi!*\n\n"
                f"👤 *O‘quvchi:* {full_name}\n"
                f"🎓 *Guruh:* {group_id}\n"
                f"💰 *Summa:* {amount:,} so‘m\n"  # Added thousands separator
                f"📅 *Sana:* {payment_date}"
            )
            await message.answer(success_message)

            # Notify student
            try:
                student_notification = (
                    "📢 Hurmatli o‘quvchi! Sizga yangi to‘lov qo‘shildi:\n\n"
                    f"💰 Summa: {amount:,} so‘m\n"
                    f"📅 Sana: {payment_date}\n\n"
                    "Savollar bo‘lsa, administratorga murojaat qiling!"
                )
                await bot.send_message(student_id, student_notification)
            except Exception as e:
                await message.answer(
                    f"⚠️ {full_name} ({group_id}) ga xabar yuborishda xatolik!\n"
                    "Sabab: Foydalanuvchi botni bloklagan bo‘lishi mumkin."
                )
        else:
            await message.answer(
                "❌ Xatolik! To‘lov ma’lumotlar bazasiga qo‘shilmadi.\n"
                "Iltimos, qayta urinib ko‘ring yoki administratorga murojaat qiling."
            )

    except Exception as e:
        await message.answer(
            "❌ Noma’lum xatolik yuz berdi!\n"
            f"Xato tafsilotlari: {str(e)}"
        )
    finally:
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


import asyncio
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_payment_reminders(bot, pyment_db, user_db, interval_seconds: float = 86400.0):
    """
    Monitors payments and updates user status:
    - Sends reminders every day to users who haven't paid
    - Changes status from 'faol' to 'faolsiz' 30 days after last payment for users who have paid

    Args:
        bot: Telegram bot instance
        pyment_db: Payment database instance
        user_db: Student database instance
        interval_seconds: Check interval in seconds (default: 86400.0 = 1 day)
    """
    last_reminder_sent = {}

    while True:
        try:
            current_time = datetime.now()

            # Get all students
            all_students = user_db.get_all_students()

            for student in all_students:
                telegram_id = student[0]

                # Get last payment info
                last_payment = pyment_db.get_payments_by_user(telegram_id)

                # Case 1: No payments found
                if not last_payment:
                    user_status = user_db.get_user_status(telegram_id)
                    if user_status != "faolsiz":
                        user_db.update_user_status(telegram_id, "faolsiz")
                        logger.info(f"Status updated to 'faolsiz' due to no payments: telegram_id={telegram_id}")

                    # Send reminder every day to users who haven't paid
                    last_sent = last_reminder_sent.get(telegram_id)
                    if not last_sent or (current_time - last_sent) >= timedelta(days=1):  # Every day
                        try:
                            await bot.send_message(
                                telegram_id,
                                "📢 Hurmatli talaba! Siz hali to‘lov qilmagansiz. "
                                "Iltimos, to‘lovni tez orada amalga oshiring!"
                            )
                            last_reminder_sent[telegram_id] = current_time
                            logger.info(f"Payment reminder sent: telegram_id={telegram_id}")
                        except Exception as e:
                            logger.error(f"Failed to send reminder: telegram_id={telegram_id}, error={str(e)}")
                    continue

                # Case 2: User has payments, check the latest one
                latest_payment = max(last_payment, key=lambda x: x[2])  # Get most recent payment by created_at
                payment_date = latest_payment[2]  # created_at field
                days_since_payment = (current_time - payment_date).days

                # If payment is older than 30 days, change status to faolsiz
                if days_since_payment >= 30:
                    current_status = user_db.get_user_status(telegram_id)
                    if current_status == "faol":
                        user_db.update_user_status(telegram_id, "faolsiz")
                        logger.info(f"Status changed to 'faolsiz' after 30 days: telegram_id={telegram_id}")
                        try:
                            await bot.send_message(
                                telegram_id,
                                "📢 Hurmatli talaba! Sizning oxirgi to‘lovingizdan 30 kun o‘tdi. "
                                "Statusingiz 'faolsiz'ga o‘zgartirildi. Iltimos, yangi to‘lov qiling!"
                            )
                            last_reminder_sent[telegram_id] = current_time
                            logger.info(f"30-day expiration notice sent: telegram_id={telegram_id}")
                        except Exception as e:
                            logger.error(f"Failed to send expiration notice: telegram_id={telegram_id}, error={str(e)}")
                # No reminders for paid users unless their payment expires (handled above)

            # Wait before next check
            await asyncio.sleep(interval_seconds)

        except Exception as e:
            logger.error(f"Payment monitoring error: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying on error

if __name__ == "__main__":
    # Mock bot and DB classes for demonstration
    class MockBot:
        async def send_message(self, telegram_id, message):
            print(f"Sending to {telegram_id}: {message}")

    class MockPaymentDB:
        def get_payments_by_user(self, telegram_id):
            # Simulate one user with a payment and one without
            if telegram_id == 123:
                return []  # No payments for user 123
            elif telegram_id == 456:
                # Payment 35 days ago for user 456
                return [(1000, "completed", datetime.now() - timedelta(days=35))]
            return []

    class MockUserDB:
        def get_all_students(self):
            return [(123, "User_123"), (456, "User_456")]

        def get_user_status(self, telegram_id):
            # Initial status for both users
            return "faol"

        def update_user_status(self, telegram_id, status):
            print(f"Updated status for {telegram_id} to {status}")

    bot = MockBot()
    pyment_db = MockPaymentDB()
    user_db = MockUserDB()

    # Run the function
    asyncio.run(send_payment_reminders(bot, pyment_db, user_db, interval_seconds=86400.0))