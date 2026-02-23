import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

# =================== Параметрлер ===================
API_TOKEN = "8757577500:AAG7FNMvw54vsg9s343MB-DDCU9kOPS-Esk"       # Мысалы: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
ADMIN_ID = 6303091468                   # Сенің Telegram ID
CHANNEL_USERNAME = "@kazakcombots"  # Сенің канал username
# ===================================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# =================== DATABASE ===================
async def init_db():
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file TEXT
            )
        """)
        await db.commit()

# =================== Каналға тіркелуді тексеру ===================
async def check_subscription(user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
    except:
        return False

# =================== Бастау командасы ===================
@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        await db.commit()

    is_subscribed = await check_subscription(user_id)

    if not is_subscribed:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📢 Каналга жазылу")],
                [KeyboardButton(text="✅ Тексеру")]
            ],
            resize_keyboard=True
        )
        await message.answer("❗ Ботты қолдану үшін каналға тіркелу керек.", reply_markup=keyboard)
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📸 Фото көру"), KeyboardButton(text="🎥 Видео көру")]],
            resize_keyboard=True
        )
        await message.answer("✅ Қош келдің! Бот жұмыс істеп тұр 🚀", reply_markup=keyboard)

# =================== Тексеру батырмасы ===================
@dp.message(F.text == "✅ Тексеру")
async def check_sub_handler(message: Message):
    user_id = message.from_user.id
    is_subscribed = await check_subscription(user_id)
    if is_subscribed:
        await message.answer("✅ Рақмет! Енді ботты қолдана аласыз.")
    else:
        await message.answer("❌ Әлі тіркелмегенсің! Каналга жазылып, қайта тексер.")

# =================== Фото / Видео батырмалары ===================
@dp.message(F.text == "🎥 Видео көру")
async def show_videos(message: Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        await message.answer("❌ Алдымен каналға тіркелу керек.")
        return

    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT file FROM videos") as cursor:
            videos = await cursor.fetchall()
            if videos:
                for video in videos:
                    await message.answer(video[0])
            else:
                await message.answer("Видео әлі қосылмаған.")

@dp.message(F.text == "📸 Фото көру")
async def show_photos(message: Message):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        await message.answer("❌ Алдымен каналға тіркелу керек.")
        return

    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT file FROM photos") as cursor:
            photos = await cursor.fetchall()
            if photos:
                for photo in photos:
                    await message.answer(photo[0])
            else:
                await message.answer("Фото әлі қосылмаған.")

# =================== Админ панелі ===================
@dp.message(F.from_user.id == ADMIN_ID)
async def admin_panel(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✏️ Видео қосу"), KeyboardButton(text="🖼 Фото қосу")],
            [KeyboardButton(text="👥 Қолданушылар санын көру")]
        ],
        resize_keyboard=True
    )
    await message.answer("🛠 Админ панелі", reply_markup=keyboard)

# =================== Видео қосу ===================
@dp.message(F.text == "✏️ Видео қосу", F.from_user.id == ADMIN_ID)
async def add_video(message: Message):
    await message.answer("Видео сілтемесін жіберіңіз:")
    dp.register_message_handler(save_video, F.from_user.id == ADMIN_ID, state=None)

async def save_video(message: Message):
    video_url = message.text
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT INTO videos (file) VALUES (?)", (video_url,))
        await db.commit()
    await message.answer("✅ Видео қосылды!")

# =================== Фото қосу ===================
@dp.message(F.text == "🖼 Фото қосу", F.from_user.id == ADMIN_ID)
async def add_photo(message: Message):
    await message.answer("Фото сілтемесін жіберіңіз:")
    dp.register_message_handler(save_photo, F.from_user.id == ADMIN_ID, state=None)

async def save_photo(message: Message):
    photo_url = message.text
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT INTO photos (file) VALUES (?)", (photo_url,))
        await db.commit()
    await message.answer("✅ Фото қосылды!")

# =================== Қолданушылар санын көру ===================
@dp.message(F.text == "👥 Қолданушылар санын көру", F.from_user.id == ADMIN_ID)
async def user_count(message: Message):
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            count = await cursor.fetchone()
            await message.answer(f"👥 Қолданушылар саны: {count[0]}")

# =================== MAIN ===================
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
