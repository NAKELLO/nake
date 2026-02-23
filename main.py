import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

# ====== VARIABLES ======
API_TOKEN = "BOT_TOKEN"      # Мұнда өз токеніңді қойасың
ADMIN_ID = 123456789         # Өз Telegram ID (админ)
CHANNEL_USERNAME = "@channelusername"  # Ботқа тіркеу керек канал
DB_PATH = "bot_database.db"
# ========================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ====== Кнопкалар ======
def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎥 Видео"), KeyboardButton(text="📸 Фото")],
        ],
        resize_keyboard=True
    )

def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Жаңа Видео"), KeyboardButton(text="Жаңа Фото")],
            [KeyboardButton(text="Қолданушылар саны")]
        ],
        resize_keyboard=True
    )

# ====== DB Инициализация ======
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY AUTOINCREMENT, file TEXT)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS photos (id INTEGER PRIMARY KEY AUTOINCREMENT, file TEXT)""")
        await db.commit()

# ====== Каналға жазылуды тексеру ======
async def check_subscription(user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except:
        return False

# ====== Қолданушыны қосу ======
async def add_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        await db.commit()

async def get_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

# ====== Видео / Фото ======
async def add_video(file: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO videos (file) VALUES (?)", (file,))
        await db.commit()

async def add_photo(file: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO photos (file) VALUES (?)", (file,))
        await db.commit()

async def get_videos():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT file FROM videos")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def get_photos():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT file FROM photos")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

# ====== /start ======
@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    await add_user(user_id)

    is_subscribed = await check_subscription(user_id)
    if not is_subscribed:
        await message.answer(f"❗ Ботты қолдану үшін каналға тіркелу керек: https://t.me/{CHANNEL_USERNAME.replace('@','')}")
        return

    if user_id == ADMIN_ID:
        await message.answer("⚙ Админ панельге қош келдің!", reply_markup=admin_keyboard())
    else:
        await message.answer("✅ Қош келдің! Бот жұмыс істеп тұр 🚀", reply_markup=main_keyboard())

# ====== Button handler ======
@dp.message()
async def buttons_handler(message: Message):
    user_id = message.from_user.id

    # === Админ ===
    if user_id == ADMIN_ID:
        if message.text == "Жаңа Видео":
            await message.answer("📤 Видео жүктеңіз (URL немесе file_id):")
            dp.register_message_handler(admin_add_video, lambda m: True, state=None)
            return
        elif message.text == "Жаңа Фото":
            await message.answer("📤 Фото жүктеңіз (URL немесе file_id):")
            dp.register_message_handler(admin_add_photo, lambda m: True, state=None)
            return
        elif message.text == "Қолданушылар саны":
            users = await get_users()
            await message.answer(f"👤 Қолданушылар саны: {len(users)}\nID тізімі:\n{users}")
        return

    # === Пайдаланушы ===
    if message.text == "🎥 Видео":
        videos = await get_videos()
        if not videos:
            await message.answer("❌ Видео әлі жоқ.")
        else:
            for v in videos:
                await message.answer_video(v)
    elif message.text == "📸 Фото":
        photos = await get_photos()
        if not photos:
            await message.answer("❌ Фото әлі жоқ.")
        else:
            for p in photos:
                await message.answer_photo(p)

# ====== Admin handlers ======
async def admin_add_video(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await add_video(message.text)
    await message.answer("✅ Видео қосылды!")

async def admin_add_photo(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await add_photo(message.text)
    await message.answer("✅ Фото қосылды!")

# ====== Run bot ======
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
