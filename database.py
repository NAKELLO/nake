import sqlite3

DB_NAME = "bot.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, ref TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS bonuses (user_id TEXT PRIMARY KEY, bonus INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY AUTOINCREMENT, file_id TEXT)")
        conn.commit()

def add_user(user_id, ref=None):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, ref) VALUES (?, ?)", (user_id, ref))
        c.execute("INSERT OR IGNORE INTO bonuses (user_id, bonus) VALUES (?, ?)", (user_id, 2))
        conn.commit()

def add_bonus(user_id, amount):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO bonuses (user_id, bonus) VALUES (?, ?)", (user_id, 0))
        c.execute("UPDATE bonuses SET bonus = bonus + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

def get_bonus(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT bonus FROM bonuses WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return row[0] if row else 0

def decrease_bonus(user_id, amount):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("UPDATE bonuses SET bonus = bonus - ? WHERE user_id = ?", (amount, user_id))
        conn.commit()

def get_all_users():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        return [row[0] for row in c.fetchall()]

def add_video(file_id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO videos (file_id) VALUES (?)", (file_id,))
        conn.commit()

def get_first_video():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT file_id FROM videos ORDER BY id ASC LIMIT 1")
        row = c.fetchone()
        return row[0] if row else None
