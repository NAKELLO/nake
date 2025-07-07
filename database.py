import sqlite3
import random

def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        invited_by TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS bonus (
        user_id TEXT PRIMARY KEY,
        amount INTEGER
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id TEXT,
        type TEXT
    )""")
    conn.commit()
    conn.close()

def add_user(user_id, invited_by=None):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, invited_by) VALUES (?, ?)", (user_id, invited_by))
    c.execute("INSERT OR IGNORE INTO bonus (user_id, amount) VALUES (?, ?)", (user_id, 2))
    conn.commit()
    conn.close()

def add_bonus(user_id, amount):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE bonus SET amount = amount + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def decrease_bonus(user_id, amount):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE bonus SET amount = amount - ? WHERE user_id = ? AND amount >= ?", (amount, user_id, amount))
    conn.commit()
    conn.close()

def get_bonus(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT amount FROM bonus WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def add_video(file_id, video_type):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT INTO videos (file_id, type) VALUES (?, ?)", (file_id, video_type))
    conn.commit()
    conn.close()

def get_random_video(video_type):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT file_id FROM videos WHERE type = ?", (video_type,))
    videos = c.fetchall()
    conn.close()
    return random.choice(videos)[0] if videos else None
