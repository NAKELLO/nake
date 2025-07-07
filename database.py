import sqlite3

def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        referrer_id TEXT,
        bonus INTEGER DEFAULT 2
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id TEXT,
        video_type TEXT
    )''')
    conn.commit()
    conn.close()

def add_user(user_id, referrer_id=None):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, referrer_id) VALUES (?, ?)", (user_id, referrer_id))
    conn.commit()
    conn.close()

def get_bonus(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT bonus FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def add_bonus(user_id, amount):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET bonus = bonus + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def decrease_bonus(user_id, amount):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET bonus = bonus - ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def add_video(file_id, video_type):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT INTO videos (file_id, video_type) VALUES (?, ?)", (file_id, video_type))
    conn.commit()
    conn.close()

def get_random_video(video_type):
    import random
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT file_id FROM videos WHERE video_type = ?", (video_type,))
    videos = c.fetchall()
    conn.close()
    if not videos:
        return None
    return random.choice(videos)[0]
