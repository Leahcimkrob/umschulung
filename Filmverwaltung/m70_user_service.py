import sqlite3

class UserService:
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            rental_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        )''')
        conn.commit()
        conn.close()

    def add_user(self, username, password, is_admin=0):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, is_admin))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return False
        conn.close()
        return True

    def get_all_users(self, with_password=False):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        if with_password:
            cur.execute("SELECT id, username, password, is_admin FROM users ORDER BY username ASC")
        else:
            cur.execute("SELECT id, username, is_admin FROM users ORDER BY username ASC")
        users = cur.fetchall()
        conn.close()
        return users

    def get_user_by_username(self, username):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, is_admin FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()
        return user

    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, is_admin FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        conn.close()
        return user

    def update_user(self, user_id, username, password, is_admin=0):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute("UPDATE users SET username = ?, password = ?, is_admin = ? WHERE id = ?", (username, password, is_admin, user_id))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return False
        conn.close()
        return True

    def delete_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

    def add_rental(self, user_id, book_id, rental_date, return_date=None):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # Prüfen, ob der Nutzer den Film bereits ausgeliehen hat und die Ausleihe noch nicht zurückgegeben wurde
        cur.execute("SELECT id FROM rentals WHERE user_id = ? AND book_id = ? AND return_date IS NULL", (user_id, book_id))
        already_rented = cur.fetchone()
        if already_rented:
            conn.close()
            return False  # Ausleihe nicht erneut speichern
        cur.execute("INSERT INTO rentals (user_id, book_id, rental_date, return_date) VALUES (?, ?, ?, ?)",
                    (user_id, book_id, rental_date, return_date))
        conn.commit()
        conn.close()
        return True

    def get_rentals_by_user_id(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT r.id, r.book_id, r.rental_date, r.return_date FROM rentals r JOIN users u ON r.user_id = u.id WHERE u.id = ?", (user_id,))
        rentals = cur.fetchall()
        conn.close()
        return rentals

    def get_all_rentals(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT r.id, u.username, r.book_id, r.rental_date, r.return_date FROM rentals r JOIN users u ON r.user_id = u.id")
        rentals = cur.fetchall()
        conn.close()
        return rentals

    def delete_rental(self, rental_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM rentals WHERE id = ?", (rental_id,))
        conn.commit()
        conn.close()

    def return_rental(self, rental_id):
        from datetime import datetime
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        return_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("UPDATE rentals SET return_date = ? WHERE id = ?", (return_date, rental_id))
        conn.commit()
        conn.close()
