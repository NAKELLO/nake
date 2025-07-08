import os
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.types import Message
from aiogram.utils import executor

API_TOKEN = os.getenv("API_TOKEN")  # Railway-де ENV арқылы
ADMIN_ID = 7702280273  # Сіздің Telegram ID (тексеру үшін)

# Лог жүргізу
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Дерекқор
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT
)
''')
conn.commit()

# Командалар
@dp.message_handler(commands=['start'])
async def start(message: Message):
    user = message.from_user
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)', (
        user.id, user.username, user.first_name, user.last_name
    ))
    conn.commit()
    await message.answer("Сәлем! Бұл бот Railway-де жұмыс істеп тұр.")

@dp.message_handler(F.text == "VIP")
async def vip(message: Message):
    await message.answer("👑 VIP Бонустар сатып алу:\n\n50 бонус = 2000тг\n100 бонус = 4000тг\n\nСатып алу үшін: @KazHubALU")

@dp.message_handler(F.text == "Қолданушы саны", F.from_user.id == ADMIN_ID)
async def count_users(message: Message):
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    await message.answer(f"👥 Қолданушылар саны: {count}")

@dp.message_handler(F.text == "Рассылка", F.from_user.id == ADMIN_ID)
async def start_broadcast(message: Message):
    await message.answer("✉️ Хабарламаңызды жіберіңіз (барлық қолданушыларға таратылады).")

@dp.message_handler(F.from_user.id == ADMIN_ID, content_types=types.ContentType.TEXT)
async def broadcast_text(message: Message):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    for user in users:
        try:
            await bot.send_message(user[0], message.text)
        except Exception as e:
            logging.error(f"Қате: {e}")
    await message.answer("✅ Барлығына жіберілді.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
