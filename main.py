import os
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.types import Message
from aiogram.utils import executor  # executor импорттау

API_TOKEN = '7748542247:AAGVgKPaOvHH7iDL4Uei2hM_zsI_6gCowkM'  # Сіздің API токеніңіз
ADMIN_ID = 7702280273  # Сіздің әкімші идентификаторыңыз

# Лог жазу конфигурациясы
logging.basicConfig(
    filename='bot.log',  # Лог файлының аты
    level=logging.INFO,  # Лог деңгейі
    format='%(asctime)s - %(levelname)s - %(message)s'  # Лог форматы
)

# Ботты және диспетчерді инициализациялау
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# SQLite дерекқорын қосу
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# `users` кестесін құру
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT
)
''')
conn.commit()

# 👑 VIP батырмасы
@dp.message(F.text == "VIP")
async def vip(message: Message):
    logging.info(f"User {message.from_user.id} requested VIP.")
    await message.answer("👑 VIP Бонустар сатып алу:\n\n50 бонус = 2000тг\n100 бонус = 4000тг\n\nСатып алу үшін: @KazHubALU")

# 👥 Қолданушы саны
@dp.message(F.text == "Қолданушы саны", F.from_user.id == ADMIN_ID)
async def count_users(message: Message):
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    logging.info(f"Admin {ADMIN_ID} requested user count: {count}.")
    await message.answer(f"👥 Қолданушылар саны: {count}")

# 📣 Рассылка
@dp.message(F.text == "Рассылка", F.from_user.id == ADMIN_ID)
async def start_broadcast(message: Message):
    logging.info(f"Admin {ADMIN_ID} started a broadcast.")
    await message.answer("✉️ Хабарламаңызды жіберіңіз (барлық қолданушыларға таратылады).")

@dp.message(F.from_user.id == ADMIN_ID, content_types=types.ContentType.TEXT)
async def broadcast_text(message: Message):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    for user in users:
        try:
            await bot.send_message(user[0], message.text)
            logging.info(f"Message sent to user {user[0]}.")
        except Exception as e:
            logging.error(f"Error sending message to {user[0]}: {e}")
    await message.answer("✅ Барлығына жіберілді.")

# 📂 Папка жасау
if not os.path.exists("saved_videos"):
    os.makedirs("saved_videos")

# 🔄 Старт
if __name__ == '__main__':
    logging.info("Bot started.")
    executor.start_polling(dp, skip_updates=True)  # executor арқылы polling бастау
