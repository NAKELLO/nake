import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.markdown import hbold

API_TOKEN = "7748542247:AAGVgKPaOvHH7iDL4Uei2hM_zsI_6gCowkM"
ADMIN_ID = 7702280273
CHANNELS = ["@oqigalaruyatsiz", "@Qazhuboyndar"]

bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# --- Database ---
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    bonus INTEGER DEFAULT 2,
    invited_by INTEGER
)
""")
conn.commit()


# --- Keyboards ---
def main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="▶️ Смотреть")
    kb.button(text="💎 Заработать")
    kb.button(text="🌸 PREMIUM")
    kb.button(text="🛍 Магазин")
    kb.button(text="🔥 Жанр")
    kb.button(text="💎 Баланс")
    return kb.as_markup(resize_keyboard=True)


# --- Handlers ---
@dp.message(F.text == "/start")
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        # Реферал коды
        referrer = message.text.split()[1] if len(message.text.split()) > 1 else None
        invited_by = int(referrer) if referrer and referrer.isdigit() else None

        cursor.execute(
            "INSERT INTO users (user_id, username, first_name, bonus, invited_by) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, first_name, 2, invited_by)
        )
        conn.commit()

        if invited_by:
            cursor.execute("UPDATE users SET bonus = bonus + 2 WHERE user_id = ?", (invited_by,))
            conn.commit()
            await bot.send_message(invited_by, f"🎉 Жаңа қолданушы тіркелді! Сізге 2 бонус берілді!")

    await message.answer("Қош келдің! Мәзірден таңдаңыз:", reply_markup=main_keyboard())


@dp.message(F.text == "💎 Баланс")
async def balance_handler(message: Message):
    cursor.execute("SELECT bonus FROM users WHERE user_id = ?", (message.from_user.id,))
    bonus = cursor.fetchone()[0]
    await message.answer(f"💰 Сіздің бонусыңыз: <b>{bonus}</b>")


@dp.message(F.text == "🌸 PREMIUM")
async def premium_handler(message: Message):
    await message.answer("👑 VIP Бонустар:\n\n50 бонус = 2000тг\n100 бонус = 4000тг\n\nСатып алу үшін: @KazHubALU")


@dp.message(F.text == "💎 Заработать")
async def earn_handler(message: Message):
    cursor.execute("UPDATE users SET bonus = bonus + 2 WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    await message.answer("✅ 2 бонус берілді! Тағы дос шақырыңыз: \nСіздің сілтемеңіз:\n"
                         f"https://t.me/Darvinuyatszdaribot?start={message.from_user.id}")


@dp.message(F.text == "▶️ Смотреть")
async def watch_handler(message: Message):
    cursor.execute("SELECT bonus FROM users WHERE user_id = ?", (message.from_user.id,))
    bonus = cursor.fetchone()[0]
    if bonus < 3:
        await message.answer("❌ Көру үшін бонус жетпейді. '💎 Заработать' арқылы алыңыз.")
        return

    cursor.execute("UPDATE users SET bonus = bonus - 3 WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    await message.answer("🎬 Міне видео:\nhttps://t.me/your_channel/video_link")


@dp.message(F.text == "🛍 Магазин")
async def shop_handler(message: Message):
    await message.answer("🛒 Жақында қосылады...")


@dp.message(F.text == "🔥 Жанр")
async def genre_handler(message: Message):
    await message.answer("🎭 Жанр таңдауы жақында болады.")


# --- Admin handlers ---
@dp.message(F.text == "Қолданушы саны", F.from_user.id == ADMIN_ID)
async def count_users(message: Message):
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    await message.answer(f"👥 Жалпы қолданушы саны: <b>{count}</b>")


@dp.message(F.text == "Рассылка", F.from_user.id == ADMIN_ID)
async def ask_broadcast(message: Message):
    await message.answer("✍️ Хабарлама мәтінін жазыңыз:")


@dp.message(F.from_user.id == ADMIN_ID)
async def do_broadcast(message: Message):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    for user in users:
        try:
            await bot.send_message(user[0], message.text)
        except:
            pass
    await message.answer("✅ Хабарлама жіберілді.")


# --- Run bot ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
