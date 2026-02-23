import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

# ================= CONFIG =================
API_TOKEN = "8757577500:AAG7FNMvw54vsg9s343MB-DDCU9kOPS-Esk"
ADMIN_ID = 6303091468
CHANNEL_USERNAME = "@kazakcombots"
BOT_USERNAME = "kazakcombot"
# ==========================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ================= DATABASE =================
async def init_db():
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            bonus INTEGER DEFAULT 2,
            referrer INTEGER,
            refs INTEGER DEFAULT 0,
            video_i INTEGER DEFAULT 0,
            photo_i INTEGER DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS media(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            file_id TEXT
        )
        """)
        await db.commit()

# ================= START =================
@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    args = message.text.split()

    referrer = None
    if len(args) > 1:
        try:
            referrer = int(args[1])
        except:
            pass

    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT OR IGNORE INTO users (id, referrer) VALUES (?,?)", (user_id, referrer))
        await db.commit()

        if referrer and referrer != user_id:
            await db.execute("UPDATE users SET bonus = bonus + 6, refs = refs + 1 WHERE id = ?", (referrer,))
            await db.commit()
            try:
                await bot.send_message(referrer, "🎉 Сіз жаңа адам шақырдыңыз! +6 бонус берілді!")
            except:
                pass

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎥 Видео көру"), KeyboardButton(text="📸 Фото көру")],
            [KeyboardButton(text="💎 Баланс"), KeyboardButton(text="👥 Реферал сілтеме")]
        ],
        resize_keyboard=True
    )

    await message.answer("🚀 Ботқа қош келдің!", reply_markup=kb)

# ================= BALANCE =================
@dp.message(F.text == "💎 Баланс")
async def balance(message: Message):
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT bonus FROM users WHERE id=?", (message.from_user.id,)) as c:
            b = await c.fetchone()
            await message.answer(f"💎 Сіздің бонус: {b[0]}")

# ================= REF LINK =================
@dp.message(F.text == "👥 Реферал сілтеме")
async def reflink(message: Message):
    link = f"https://t.me/{BOT_USERNAME}?start={message.from_user.id}"
    await message.answer(f"👥 Сіздің реферал сілтеме:\n{link}")

# ================= MEDIA VIEW =================
async def show_media(message: Message, mtype: str):

    user_id = message.from_user.id

    if user_id != ADMIN_ID:
        async with aiosqlite.connect("bot_database.db") as db:
            async with db.execute("SELECT bonus FROM users WHERE id=?", (user_id,)) as c:
                bonus = (await c.fetchone())[0]
                if bonus < 3:
                    await message.answer("❌ Бонус жетпейді!")
                    return
                await db.execute("UPDATE users SET bonus = bonus - 3 WHERE id=?", (user_id,))
                await db.commit()

    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT id,file_id FROM media WHERE type=? ORDER BY id", (mtype,)) as c:
            files = await c.fetchall()
            if not files:
                await message.answer("Контент жоқ.")
                return

        async with db.execute(f"SELECT {mtype}_i FROM users WHERE id=?", (user_id,)) as c:
            idx = (await c.fetchone())[0]

        file = files[idx % len(files)][1]

        await db.execute(f"UPDATE users SET {mtype}_i = {mtype}_i + 1 WHERE id=?", (user_id,))
        await db.commit()

    if mtype == "video":
        await message.answer_video(file)
    else:
        await message.answer_photo(file)

@dp.message(F.text == "🎥 Видео көру")
async def video(message: Message):
    await show_media(message, "video")

@dp.message(F.text == "📸 Фото көру")
async def photo(message: Message):
    await show_media(message, "photo")

# ================= ADMIN =================
@dp.message(F.from_user.id == ADMIN_ID)
async def admin_panel(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Видео қосу"), KeyboardButton(text="➕ Фото қосу")],
            [KeyboardButton(text="📊 Қолданушы саны"), KeyboardButton(text="🎁 Бонус беру")]
        ],
        resize_keyboard=True
    )
    await message.answer("🛠 Админ панелі", reply_markup=kb)

@dp.message(F.video, F.from_user.id == ADMIN_ID)
async def add_video(message: Message):
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT INTO media(type,file_id) VALUES('video',?)", (message.video.file_id,))
        await db.commit()
    await message.answer("✅ Видео сақталды!")

@dp.message(F.photo, F.from_user.id == ADMIN_ID)
async def add_photo(message: Message):
    file_id = message.photo[-1].file_id
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT INTO media(type,file_id) VALUES('photo',?)", (file_id,))
        await db.commit()
    await message.answer("✅ Фото сақталды!")

@dp.message(F.text == "📊 Қолданушы саны", F.from_user.id == ADMIN_ID)
async def users_count(message: Message):
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            count = (await c.fetchone())[0]
            await message.answer(f"👥 Қолданушы саны: {count}")

@dp.message(F.text.startswith("🎁"), F.from_user.id == ADMIN_ID)
async def give_bonus(message: Message):
    await message.answer("Формат: user_id бонус")

@dp.message(F.from_user.id == ADMIN_ID)
async def bonus_input(message: Message):
    try:
        user_id, amount = map(int, message.text.split())
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("UPDATE users SET bonus = bonus + ? WHERE id=?", (amount, user_id))
            await db.commit()
        await message.answer("✅ Бонус берілді!")
    except:
        pass

# ================= RUN =================
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
