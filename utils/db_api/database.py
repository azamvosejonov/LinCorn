import sqlite3
from datetime import datetime
import sys


def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")



class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db
        self.create_table_student()
        self.create_table()
        self.create_table_message()
        self.create_table_admins()
        self.create_payments_table()


    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection

        # Faqat Python 3.8 va undan yuqori versiyalar uchun logger ishlaydi
        if sys.version_info >= (3, 8):
            connection.set_trace_callback(logger)

        cursor = connection.cursor()
        data = None
        try:
            cursor.execute(sql, parameters)
            if commit:
                connection.commit()
            if fetchall:
                data = cursor.fetchall()
            if fetchone:
                data = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            if commit:
                connection.rollback()
        finally:
            connection.close()
        return data

    @staticmethod
    def format_args(sql, parameters: dict):
        if parameters:
            sql += " WHERE " + " AND ".join([f"{item} = ?" for item in parameters])
            return sql, tuple(parameters.values())
        return sql, ()

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


    def create_table(self):
        sql = """
     CREATE TABLE IF NOT EXISTS Jadval (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            updated_at INTEGER DEFAULT NULL
            );
        """
        self.execute(sql, commit=True)


    def create_table_message(self):
        sql = """
CREATE TABLE IF NOT EXISTS Messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT,
                message TEXT NOT NULL,
                group_id VARCHAR(255) ,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES Student(telegram_id) ON DELETE CASCADE
            );
            """
        self.execute(sql, commit=True)


    def create_table_admins(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT UNIQUE NOT NULL,
                full_name VARCHAR(255) NOT NULL
            );
        """
        self.execute(sql, commit=True)

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
