import sqlite3
import hashlib
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="campus_users.db"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            return True
        except Exception:
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def create_users_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception:
            return False

    def hash_password(self, password):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt + key

    def verify_password(self, password, stored_hash):
        salt = stored_hash[:32]
        key = stored_hash[32:]
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return new_key == key

    def add_user(self, username, email, password, full_name=""):
        password_hash = self.hash_password(password)
        query = "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)"
        try:
            self.cursor.execute(query, (username, email, password_hash, full_name))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_user(self, username):
        query = "SELECT id, username, email, password_hash, full_name, created_at, last_login FROM users WHERE username = ? AND is_active = 1"
        self.cursor.execute(query, (username,))
        return self.cursor.fetchone()

    def update_last_login(self, user_id):
        query = "UPDATE users SET last_login = ? WHERE id = ?"
        self.cursor.execute(query, (datetime.now(), user_id))
        self.connection.commit()

    def user_exists(self, username, email):
        query = "SELECT COUNT(*) FROM users WHERE username = ? OR email = ?"
        self.cursor.execute(query, (username, email))
        return self.cursor.fetchone()[0] > 0


if __name__ == "__main__":
    db = DatabaseManager()
    if db.connect():
        db.create_users_table()
        db.add_user("john_doe", "john@example.com", "password123", "John Doe")
        user = db.get_user("john_doe")
        if user:
            print(user[1])
        db.disconnect()