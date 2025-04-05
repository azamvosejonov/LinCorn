from datetime import datetime
from .database import Database
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram import Bot


class StudentDatabase(Database):
    def __init__(self, db_path, bot: Bot):
        super().__init__(db_path)
        self.bot = bot
    def create_table_student(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Student (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name VARCHAR(255) NOT NULL,
                telegram_id BIGINT NOT NULL,
                yosh INT NOT NULL,
                phone VARCHAR(20) NOT NULL,
                group_id VARCHAR(255),
                status VARCHAR(10) DEFAULT 'faolsiz' CHECK (status IN ('faol', 'faolsiz')),
                student_type VARCHAR(20) DEFAULT 'oddiy',
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        self.execute(sql, commit=True)




    def create_table_attendance(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Attendance (
                id SERIAL PRIMARY KEY,
                student_id INT NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(10) NOT NULL CHECK (status IN ('present', 'absent')),
                FOREIGN KEY (student_id) REFERENCES Student(id) ON DELETE CASCADE
            );
            """
        self.execute(sql, commit=True)

    def create_table_messages(self):
        sql = """
               CREATE TABLE IF NOT EXISTS Messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT,
                message TEXT NOT NULL,
                group_id VARCHAR(255),
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES Student(telegram_id) ON DELETE CASCADE
            );
           """
        self.execute(sql, commit=True)


    def add_student(self, full_name: str, group_id: str, yosh: int, phone: int, telegram_id: int):
        sql = """
            INSERT INTO Student(full_name, group_id, yosh, phone, telegram_id)
            VALUES(?,?,?,?,?)
            """
        self.execute(sql, parameters=(full_name, group_id, yosh, phone, telegram_id), commit=True)

    def mark_attendance(self, student_id: int, date: str, status: str):
        sql = """
            INSERT INTO Attendance(student_id, date, status)
            VALUES(?,?,?)
            """
        self.execute(sql, parameters=(student_id, date, status), commit=True)

    def get_absent_days(self, student_id: int):
        sql = """
            SELECT COUNT(*) FROM Attendance WHERE student_id = ? AND status = 'absent'
        """
        return self.execute(sql, parameters=(student_id,), fetchone=True)[0]

    def update_student_caption(self, full_name: str, group_id: str, yosh: int, phone: int):
        sql = """
            UPDATE Student
            SET full_name=?, group_id=?, yosh=?, phone=?
            WHERE group_id=?
            """
        self.execute(sql, parameters=(full_name, group_id, yosh, phone, group_id), commit=True)

    def delete_student_postid(self, full_name: str, group_id: str):
        sql = """
            DELETE FROM Student WHERE full_name=? AND group_id=?
        """
        self.execute(sql, parameters=(full_name, group_id), commit=True)

    def student_list(self, group_id: str):
        sql = """
            SELECT full_name, phone, group_id, yosh FROM Student WHERE group_id=?;
        """
        return self.execute(sql, parameters=(group_id,), fetchall=True)

    def count_users(self):
        sql = """
            SELECT COUNT(*) FROM Student
            """
        return self.execute(sql, fetchone=True)

    def select_student(self, telegram_id):
        sql = "SELECT * FROM Student WHERE telegram_id = ?"
        return self.execute(sql, parameters=(telegram_id,), fetchone=True)

    def student_r(self):
        sql = "SELECT full_name, group_id, yosh, phone FROM Student;"
        result = self.execute(sql, fetchall=True)
        if not result:
            return []
        return [
            {"full_name": row[0], "group_id": row[1], "yosh": row[2], "phone": row[3]}
            for row in result
        ]

    def get_all_students(self):
        sql = "SELECT telegram_id, full_name FROM Student;"  # Telegram ID va ismni olish
        return self.execute(sql, fetchall=True)

    def get_student_by_name_and_group(self, full_name: str, group_id: str):
        sql = "SELECT id FROM Student WHERE full_name = ? AND group_id = ?;"
        return self.execute(sql, parameters=(full_name, group_id), fetchone=True)

    def get_student_by_telegram_id(self, telegram_id):
        sql = "SELECT * FROM Student WHERE telegram_id = ?;"
        return self.execute(sql, parameters=(telegram_id,), fetchone=True)



    async def send_message_to_user(self, telegram_id: int, message: str):
        sql = "INSERT INTO Messages (telegram_id, message) VALUES (?, ?);"
        self.execute(sql, parameters=(telegram_id, message), commit=True)
        await self.bot.send_message(telegram_id, message)

    async def send_message_to_group(self, group_id: str, message: str):
        sql = "SELECT telegram_id FROM Student WHERE group_id = ?;"
        users = self.execute(sql, parameters=(group_id,), fetchall=True)
        for user in users:
            sql_insert = "INSERT INTO Messages (telegram_id, group_id, message) VALUES (?, ?, ?);"
            self.execute(sql_insert, parameters=(user[0], group_id, message), commit=True)
            await self.bot.send_message(user[0], message)

    async def send_message_to_all(self, message: str):
        sql = "SELECT telegram_id FROM Student;"
        users = self.execute(sql, fetchall=True)
        for user in users:
            sql_insert = "INSERT INTO Messages (telegram_id, message) VALUES (?, ?);"
            self.execute(sql_insert, parameters=(user[0], message), commit=True)
            await self.bot.send_message(user[0], message)

    def get_students_by_group(self, group_id: str):
        sql = "SELECT telegram_id, full_name FROM Student WHERE group_id = ?;"
        return self.execute(sql, parameters=(group_id,), fetchall=True)

    def get_last_messages(self, limit=10):
        sql = """
            SELECT telegram_id, group_id, message, sent_at 
            FROM Messages 
            ORDER BY sent_at DESC 
            LIMIT ?;
        """
        return self.execute(sql, parameters=(limit,), fetchall=True)

    def get_all_groups(self):
        sql = "SELECT DISTINCT group_id FROM Student;"
        return self.execute(sql, fetchall=True)

    def add_status_column(self):
        sql = "ALTER TABLE Student ADD COLUMN status VARCHAR(10) DEFAULT 'faolsiz' CHECK (status IN ('faol', 'faolsiz'));"
        self.execute(sql, commit=True)

    def update_student_status(self, telegram_id: int, status: str):
        if status not in ["faol", "faolsiz"]:
            raise ValueError("Status faqat 'faol' yoki 'faolsiz' bo'lishi mumkin!")

        sql = """
            UPDATE Student
            SET status = ?
            WHERE telegram_id = ?
        """
        self.execute(sql, parameters=(status, telegram_id), commit=True)

    def get_student_status(self, telegram_id: int):
        sql = """
            SELECT status FROM Student WHERE telegram_id = ?
        """
        result = self.execute(sql, parameters=(telegram_id,), fetchone=True)
        return result[0] if result else None

    def get_student_type(self, telegram_id: int):
        sql = "SELECT student_type FROM Student WHERE telegram_id = ?"
        result = self.execute(sql, parameters=(telegram_id,), fetchone=True)
        return result[0] if result else None

    def update_student_type(self, telegram_id: int, student_type: str):
        if student_type not in ["oddiy", "vip"]:
            raise ValueError("Tur faqat 'oddiy' yoki 'vip' bo'lishi mumkin!")

        sql = """
            UPDATE Student
            SET student_type = ?
            WHERE telegram_id = ?
        """
        self.execute(sql, parameters=(student_type, telegram_id), commit=True)

    def update_last_active(self,telegram_id: int):
        sql = """
        UPDATE Student
        SET last_active = CURRENT_TIMESTAMP
        WHERE telegram_id = ?;
        """
        self.execute(sql, parameters=(telegram_id,), commit=True)

    def get_inactive_students(self):
        sql = """
        SELECT telegram_id FROM Student
        WHERE last_active <= datetime('now', '-1 day');
        """
        return self.execute(sql, fetchall=True)



    def get_user_info(self, telegram_id):
        sql = "SELECT full_name, group_id FROM Student WHERE telegram_id = ?"
        result = self.execute(sql, (telegram_id,), fetchone=True)
        if result:
            return {"full_name": result[0], "group_id": result[1]}
        return None

    def get_user_status(self, telegram_id: int):
        """Foydalanuvchi statusini qaytaradi (faol yoki faol emas)"""
        sql = "SELECT status FROM Student WHERE telegram_id = ?"
        result = self.execute(sql, (telegram_id,), fetchone=True)
        return result[0] if result else None

    def update_user_status(self, telegram_id: int, new_status: str):
        sql = """
        UPDATE Student 
        SET status = ? 
        WHERE telegram_id = ?
        """
        self.execute(sql, (new_status, telegram_id), commit=True)

    def get_active_users(self):
        """Faol foydalanuvchilar ro‘yxatini olish."""
        query = "SELECT telegram_id, full_name, group_id, phone FROM Student WHERE status = 'faol'"
        return self.execute(query, fetchall=True)

    def get_inactive_users(self):
        """Faolsiz foydalanuvchilar ro‘yxatini olish."""
        query = "SELECT telegram_id, full_name, group_id, phone FROM Student WHERE status != 'faol'"
        return self.execute(query, fetchall=True)

    def get_student_by_name_and_groups(self, full_name: str, group_id: str):
        """ Berilgan ism va guruh ID ga mos keladigan o‘quvchini qaytaradi """
        sql = "SELECT telegram_id, full_name, group_id FROM Student WHERE full_name = ? AND group_id = ?"
        student = self.execute(sql, parameters=(full_name, group_id), fetchone=True)

        if student:
            return {
                "telegram_id": student[0],
                "full_name": student[1],
                "group_id": student[2]
            }
        return None  # Agar o‘quvchi topilmasa, None qaytariladi

    def get_students_by_name(self, full_name: str):
        """Berilgan ismga ega barcha o'quvchilarni qaytaradi"""
        sql = "SELECT telegram_id, full_name, group_id FROM Student WHERE full_name = ?"
        students = self.execute(sql, parameters=(full_name,), fetchall=True)

        # Har bir tupleni dictionary ga o'girib qaytaramiz
        return [
            {"telegram_id": student[0], "full_name": student[1], "group_id": student[2]}
            for student in students
        ]

    def get_student_by_telegram_ids(self, telegram_id: int):
        """Telegram ID bo‘yicha o‘quvchining ma’lumotlarini qaytaradi"""
        sql = "SELECT telegram_id, full_name, group_id FROM Student WHERE telegram_id = ?"
        student = self.execute(sql, parameters=(telegram_id,), fetchone=True)

        if not student:
            return None

        return {"telegram_id": student[0], "full_name": student[1], "group_id": student[2]}

    def get_students_by_status(self, status):
        """Berilgan statusga ega foydalanuvchilarni olish."""
        query = "SELECT telegram_id, full_name FROM Student WHERE status = ?"
        return self.execute(query, (status,), fetchall=True)

    def get_student_by_id(self, student_id):
        """Berilgan ID bo‘yicha o‘quvchini olish."""
        query = "SELECT telegram_id, full_name, status, group_id FROM Student WHERE telegram_id = ?"
        return self.execute(query, (student_id,), fetchone=True)

    def get_messages_by_telegram_id(self, telegram_id: int):
        """Foydalanuvchiga yuborilgan barcha xabarlarni olish."""
        sql = """
            SELECT message, sent_at 
            FROM Messages 
            WHERE telegram_id = ? 
            ORDER BY sent_at DESC;
        """
        return self.execute(sql, parameters=(telegram_id,), fetchall=True)

    def get_student_statusi(self, telegram_id: int):
        """Foydalanuvchining statusini bazadan olish."""
        sql = "SELECT status FROM Student WHERE telegram_id = ?"
        result = self.execute(sql, (telegram_id,), fetchone=True)

        if result:
            return result[0]  # faqat statusni qaytaradi ('faol' yoki boshqa holatlar)

        return None  # Agar foydalanuvchi bazada bo‘lmasa










