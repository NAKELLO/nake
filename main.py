import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

# =================== Параметрлер ===================
API_TOKEN = "8757577500:AAG7FNMvw54vsg9s343MB-DDCU9kOPS-Esk"
BOT_USERNAME = "kazakcombot"
ADMIN_ID = 6303091468
CHANNEL_USERNAME = "@kazakcombots"
# ====================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# =================== DATABASE ===================
async def init_db():
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                referrer_id INTEGER,
                bonus INTEGER DEFAULT 2,
                referral_count INTEGER DEFAULT 0
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

# =================== Каналға жазылу тексеру ===================
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

# =================== Бастау + реферал ===================
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    ref_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (id, referrer_id, bonus) VALUES (?, ?, ?)", (user_id, ref_id, 2))
        if ref_id:
            await db.execute("UPDATE users SET bonus = bonus + 6, referral_count = referral_count + 1 WHERE id=?", (ref_id,))
        await db.commit()

    is_subscribed = await check_subscription(user_id)
    if not is_subscribed:
        keyboard = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton("📢 Каналга жазылу")], [types.KeyboardButton("✅ Тексеру")]], resize_keyboard=True)
        await message.answer(f"❗ Ботты қолдану үшін каналға тіркелу керек.\nСіздің реферал сілтеме: t.me/{BOT_USERNAME}?start={user_id}", reply_markup=keyboard)
    else:
        keyboard = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton("📸 Фото көру"), types.KeyboardButton("🎥 Видео көру")]], resize_keyboard=True)
        await message.answer(f"✅ Қош келдің! Бот жұмыс істеп тұр 🚀\nСіздің реферал сілтеме: t.me/{BOT_USERNAME}?start={user_id}", reply_markup=keyboard)

# =================== Тексеру батырмасы ===================
@dp.message(F.text == "✅ Тексеру")
async def check_sub_handler(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)
    await message.answer("✅ Рақмет! Енді ботты қолдана аласыз." if is_subscribed else "❌ Әлі тіркелмегенсің! Каналга жазылып, қайта тексер.")

# =================== Видео / Фото көрсету ===================
async def send_content(user_id: int, table: str):
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT bonus FROM users WHERE id=?", (user_id,)) as cur:
            bonus = await cur.fetchone()
            if not bonus or bonus[0] <= 0:
                return None
        async with db.execute(f"SELECT id, file FROM {table} ORDER BY id ASC LIMIT 1") as cur:
            item = await cur.fetchone()
            if item:
                await db.execute(f"DELETE FROM {table} WHERE id=?", (item[0],))
                await db.execute("UPDATE users SET bonus = bonus - 3 WHERE id=?", (user_id,))
                await db.commit()
                return item[1]
    return None

@dp.message(F.text == "🎥 Видео көру")
async def show_videos(message: types.Message):
    video = await send_content(message.from_user.id, "videos")
    await message.answer(video if video else "❌ Бонус жоқ немесе видео жоқ.")

@dp.message(F.text == "📸 Фото көру")
async def show_photos(message: types.Message):
    photo = await send_content(message.from_user.id, "photos")
    await message.answer(photo if photo else "❌ Бонус жоқ немесе фото жоқ.")

# =================== Админ панелі ===================
@dp.message(F.from_user.id == ADMIN_ID)
async def admin_panel(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton("✏️ Видео қосу"), types.KeyboardButton("🖼 Фото қосу")],
        [types.KeyboardButton("👥 Қолданушылар санын көру")],
        [types.KeyboardButton("💎 Бонус беру")]
    ], resize_keyboard=True)
    await message.answer("🛠 Админ панелі", reply_markup=keyboard)

# =================== Админ видео/фото қосу ===================
@dp.message(F.text == "✏️ Видео қосу", F.from_user.id == ADMIN_ID)
async def add_video(message: types.Message):
    await message.answer("Видео сілтемесін немесе файлды жіберіңіз:")
    dp.register_message_handler(save_video, F.from_user.id == ADMIN_ID, state=None)

async def save_video(message: types.Message):
    video = message.text or (message.video.file_id if message.video else None)
    if video:
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("INSERT INTO videos (file) VALUES (?)", (video,))
            await db.commit()
        await message.answer("✅ Видео қосылды!")

@dp.message(F.text == "🖼 Фото қосу", F.from_user.id == ADMIN_ID)
async def add_photo(message: types.Message):
    await message.answer("Фото сілтемесін немесе файлды жіберіңіз:")
    dp.register_message_handler(save_photo, F.from_user.id == ADMIN_ID, state=None)

async def save_photo(message: types.Message):
    photo = message.text or (message.photo[-1].file_id if message.photo else None)
    if photo:
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("INSERT INTO photos (file) VALUES (?)", (photo,))
            await db.commit()
        await message.answer("✅ Фото қосылды!")

# =================== Қолданушылар санын көру ===================
@dp.message(F.text == "👥 Қолданушылар санын көру", F.from_user.id == ADMIN_ID)
async def user_count(message: types.Message):
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            count = await cur.fetchone()
            await message.answer(f"👥 Қолданушылар саны: {count[0]}")

# =================== Бонус беру ===================
@dp.message(F.text == "💎 Бонус беру", F.from_user.id == ADMIN_ID)
async def give_bonus(message: types.Message):
    await message.answer("Кімге бонус бересіз? Telegram ID және бонус сомасын енгізіңіз (мысалы: 123456789 10):")
    dp.register_message_handler(save_bonus, F.from_user.id == ADMIN_ID, state=None)

async def save_bonus(message: types.Message):
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Қате формат. Мысалы: 123456789 10")
        return
    user_id, bonus = int(parts[0]), int(parts[1])
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("UPDATE users SET bonus = bonus + ? WHERE id=?", (bonus, user_id))
        await db.commit()
    await message.answer(f"✅ {bonus} бонус {user_id} пайдаланушыға берілді!")

# =================== MAIN ===================
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
