from datetime import datetime
from .database import Database

class JadvalDatabase(Database):
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

    def add_jadval(self, title: str, date: str, start_time: str, end_time: str, timestamp: int):
        sql = """
        INSERT INTO Jadval (title, date, start_time, end_time, timestamp) 
        VALUES (?, ?, ?, ?, ?)
        """
        self.execute(sql, parameters=(title, date, start_time, end_time, timestamp), commit=True)


    def get_jadval(self):
        sql = "SELECT * FROM Jadval ORDER BY date ASC, start_time ASC"
        return self.execute(sql, fetchall=True)

    def update_jadval(self, jadval_id, title, date, start_time, end_time):
        sql = """
        UPDATE Jadval SET title = ?, date = ?, start_time = ?, end_time = ?, updated_at = ? 
        WHERE id = ?
        """
        updated_at = int(datetime.now().timestamp())
        self.execute(sql, parameters=(title, date, start_time, end_time, updated_at, jadval_id), commit=True)

    def delete_jadval(self, jadval_id):
        sql = "DELETE FROM Jadval WHERE id = ?"
        self.execute(sql, parameters=(jadval_id,), commit=True)

    def get_upcoming_lessons(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        sql = """
           SELECT * FROM Jadval 
           WHERE (date > ?) OR (date = ? AND start_time >= ?) 
           ORDER BY date ASC, start_time ASC
           """
        return self.execute(sql, parameters=(current_date, current_date, current_time), fetchall=True)

    def get_past_lessons(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        sql = """
           SELECT * FROM Jadval 
           WHERE (date < ?) OR (date = ? AND end_time < ?)
           ORDER BY date DESC, end_time DESC
           """
        return self.execute(sql, parameters=(current_date, current_date, current_time), fetchall=True)

    def get_lessons_by_title(self, title):
        sql = """
           SELECT * FROM Jadval WHERE title LIKE ? ORDER BY date ASC, start_time ASC
        """
        return self.execute(sql, parameters=(f"%{title}%",), fetchall=True)

    def delete_old_lessons(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        sql = """
            DELETE FROM Jadval 
            WHERE date < ?
        """
        self.execute(sql, parameters=(current_date,), commit=True)