import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import CommandStart
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3

API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'
ADMIN_ID = 6927494520
CHANNEL_USERNAME = "@darvinteioria"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# База
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, bonus INTEGER DEFAULT 0, referrer_id INTEGER)")
conn.commit()

# Функция: каналға тіркелген бе?
async def check_subscription(user_id):
    member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    return member.status in ['member', 'creator', 'administrator']

# Старт
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if not await check_subscription(user_id):
        return await message.answer("Алдымен каналға тіркеліңіз: @darvinteioria")

    if not user:
        referrer_id = int(args) if args.isdigit() else None
        cursor.execute("INSERT INTO users (id, bonus, referrer_id) VALUES (?, ?, ?)", (user_id, 2, referrer_id))
        if referrer_id:
            cursor.execute("UPDATE users SET bonus = bonus + 1 WHERE id = ?", (referrer_id,))
        conn.commit()
        await message.answer("Тіркелдіңіз! Сізге 2 бонус жазылды ✅")
    else:
        await message.answer("Қайта оралдыңыз!")

    referral_link = f"https://t.me/Darvinuyatszdaribot?start={user_id}"
    cursor.execute("SELECT bonus FROM users WHERE id=?", (user_id,))
    bonus = cursor.fetchone()[0]
    await message.answer(f"Сізде {bonus} бонус бар.\nСілтемеңіз: {referral_link}")

# Бонус көру
@dp.message_handler(commands=['bonus'])
async def bonus_handler(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT bonus FROM users WHERE id=?", (user_id,))
    result = cursor.fetchone()
    bonus = result[0] if result else 0
    await message.answer(f"Сізде {bonus} бонус бар.")

# Админге статистика
@dp.message_handler(commands=['stats'])
async def stats_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    await message.answer(f"Жүйеде {total} қолданушы бар.")

if name == 'main':
    executor.start_polling(dp, skip_updates=True)
