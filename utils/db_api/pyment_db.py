from datetime import datetime, timedelta
from .database import Database

class PymentDatabase(Database):

    def create_payments_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT NOT NULL REFERENCES Student(telegram_id) ON DELETE CASCADE,
            amount DECIMAL(10,2),
            status TEXT DEFAULT 'pending',
            receipt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payment_date TEXT
        );
        """
        self.execute(sql, commit=True)

    # ✅ To‘lov cheki saqlash
    def save_payment_receipt(self, telegram_id, file_id):
        sql = """
        INSERT INTO Payments (telegram_id, receipt, status, created_at) 
        VALUES (?, ?, 'pending', CURRENT_TIMESTAMP)
        """
        self.execute(sql, (telegram_id, file_id), commit=True)

    # ✅ To‘lovni tasdiqlash
    def confirm_payment(self, telegram_id: int):
        sql = """
        UPDATE Payments 
        SET status = 'completed' 
        WHERE telegram_id = ?
        """
        self.execute(sql, (telegram_id,), commit=True)

        sql_student = """
        UPDATE Student 
        SET status = 'faol' 
        WHERE telegram_id = ?
        """
        self.execute(sql_student, (telegram_id,), commit=True)

    # ❌ To‘lovni rad etish
    def reject_payment(self, telegram_id: int):
        sql = """
        UPDATE Payments 
        SET status = 'rejected' 
        WHERE telegram_id = ?
        """
        self.execute(sql, (telegram_id,), commit=True)

    # ✅ 1 oy davomida to‘lov qilmaganlarni olish
    def get_due_payments(self):
        one_month_ago = datetime.now() - timedelta(days=30)
        sql = """
        SELECT telegram_id FROM Payments 
        WHERE status = 'pending' AND created_at <= ?
        """
        return self.execute(sql, (one_month_ago,), fetchall=True)

    # ✅ Talaba "faol" yoki yo‘qligini tekshirish
    def is_student_active(self, telegram_id: int):
        sql = "SELECT status FROM Student WHERE telegram_id = ?"
        result = self.execute(sql, (telegram_id,), fetchone=True)
        return result[0] == 'faol' if result else False

    # ✅ Superadmin ID sini olish
    def get_all_payments(self):
        """Barcha to‘lov qilgan foydalanuvchilarning ID va sanasini qaytaradi."""
        query = "SELECT telegram_id, created_at FROM Payments WHERE status = 'completed'"
        return self.execute(query, fetchall=True)

    def delete_payment(self, telegram_id):
        """Foydalanuvchi to‘lovini o‘chirish."""
        query = "DELETE FROM Payments WHERE telegram_id = ?"
        self.execute(query, (telegram_id,), commit=True)
        return True

    def add_payment(self, telegram_id: int, amount: float, payment_date: str):
        """Foydalanuvchining to‘lovini qo‘shish."""
        try:
            query = """
            INSERT INTO Payments (telegram_id, amount, receipt, status, created_at, payment_date) 
            VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP, ?)
            """
            self.execute(query, (telegram_id, amount, payment_date), commit=True)
            return True
        except Exception as e:
            print(f"❌ Xatolik: {e}")
            return False

    def get_payments_by_student_id(self, student_id: int):
        """Berilgan student ID bo‘yicha barcha to‘lovlarni qaytaradi"""
        sql = "SELECT payment_date, amount FROM Payments WHERE student_id = ? ORDER BY payment_date DESC"
        payments = self.execute(sql, parameters=(student_id,), fetchall=True)

        # Agar bazadan hech narsa topilmasa, bo‘sh ro‘yxat qaytaramiz (None emas!)
        if payments is None:
            return []

        return [{"payment_date": payment[0], "amount": payment[1]} for payment in payments]

    def get_admin_added_payments_by_telegram_id(self, telegram_id: int):
        """Telegram ID bo‘yicha faqat admin tomonidan qo‘shilgan to‘lovlarni qaytaradi"""
        sql = """
        SELECT payment_date, amount, admin_id FROM Payments 
        WHERE telegram_id = (SELECT id FROM Student WHERE telegram_id = ?) 
        AND admin_id IS NOT NULL
        ORDER BY payment_date DESC
        """
        payments = self.execute(sql, parameters=(telegram_id,), fetchall=True)

        if not payments:
            return []

        return [{"payment_date": payment[0], "amount": payment[1], "admin_id": payment[2]} for payment in payments]

    def get_payment_dates(self, telegram_id: int):
        """Foydalanuvchining barcha to‘lov sanalarini chiqaradi."""
        sql = """
        SELECT payment_date 
        FROM Payments 
        WHERE telegram_id = ? 
        ORDER BY created_at DESC
        """
        payments = self.execute(sql, (telegram_id,), fetchall=True)

        if not payments:
            return "📭 Sizning to‘lov tarixingiz topilmadi!"

        return [payment[0] for payment in payments]  # Faqat sanalarni qaytaradi

    def get_payments_by_user(self, telegram_id: int):
        """Foydalanuvchining so‘nggi 5 kun ichidagi to‘lovlarini olish"""
        try:
            query = """
            SELECT amount, status, created_at 
            FROM Payments 
            WHERE telegram_id = ? AND created_at >= DATE('now', '-1 days')
            """
            rows = self.execute(query, (telegram_id,), fetchall=True)
            return rows
        except Exception as e:
            print(f"Xatolik: {e}")
            return []





