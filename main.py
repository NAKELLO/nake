import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

# =================== Параметрлер ===================
API_TOKEN = "8757577500:AAG7FNMvw54vsg9s343MB-DDCU9kOPS-Esk"  # Бот токен
ADMIN_ID = 6303091468                                        # Telegram ID
CHANNEL_USERNAME = "@kazakcombots"                            # Канал username
# =====================================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# =================== DATABASE ===================
async def init_db():
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                bonus INTEGER DEFAULT 0,
                ref_code TEXT UNIQUE
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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER
            )
        """)
        await db.commit()
# ================================================

# =================== Каналға тіркелу ===================
from aiogram.enums import ChatMemberStatus

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
# ================================================

# =================== Старт және реферал ===================
import random, string

def generate_ref_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    args = message.get_args()  # /start REFERRAL_CODE

    async with aiosqlite.connect("bot_database.db") as db:
        # Қолданушыны қосу
        await db.execute("INSERT OR IGNORE INTO users (id, bonus, ref_code) VALUES (?, ?, ?)",
                         (user_id, 2, generate_ref_code()))
        await db.commit()

        # Реферал қосу
        if args:
            # args = referral code
            async with db.execute("SELECT id FROM users WHERE ref_code = ?", (args,)) as cur:
                referrer = await cur.fetchone()
                if referrer:
                    # Реферерге бонус қосу
                    await db.execute("UPDATE users SET bonus = bonus + 6 WHERE id = ?", (referrer[0],))
                    await db.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
                                     (referrer[0], user_id))
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
            keyboard=[
                [KeyboardButton(text="📸 Фото көру"), KeyboardButton(text="🎥 Видео көру")],
                [KeyboardButton(text="🤑 Бонус алу"), KeyboardButton(text="🧾 Менің реферал сілтемем")]
            ],
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

# =================== Видео / Фото көрсету ===================
async def send_content(message: Message, table_name: str, cost: int):
    user_id = message.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        # Бонус тексеру
        async with db.execute("SELECT bonus FROM users WHERE id = ?", (user_id,)) as cur:
            user = await cur.fetchone()
            if not user or user[0] < cost:
                await message.answer("❌ Бонус жеткіліксіз!")
                return

        # Алма кезекпен шығару
        async with db.execute(f"SELECT file FROM {table_name} ORDER BY id ASC") as cur:
            items = await cur.fetchall()
            if not items:
                await message.answer(f"{table_name} әлі қосылмаған!")
                return
            for item in items:
                await message.answer(item[0])
                # Бонус азайту
                await db.execute("UPDATE users SET bonus = bonus - ? WHERE id = ?", (cost, user_id))
                await db.commit()

@dp.message(F.text == "🎥 Видео көру")
async def show_videos(message: Message):
    await send_content(message, "videos", 3)

@dp.message(F.text == "📸 Фото көру")
async def show_photos(message: Message):
    await send_content(message, "photos", 1)

# =================== Бонус алу ===================
@dp.message(F.text == "🤑 Бонус алу")
async def bonus_handler(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        # 2 бонус қосу
        await db.execute("UPDATE users SET bonus = bonus + 2 WHERE id = ?", (user_id,))
        await db.commit()
        await message.answer("✅ Сізге 2 бонус қосылды!")

# =================== Менің реферал сілтемем ===================
@dp.message(F.text == "🧾 Менің реферал сілтемем")
async def my_ref_handler(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT ref_code FROM users WHERE id = ?", (user_id,)) as cur:
            ref = await cur.fetchone()
            if ref:
                await message.answer(f"Сіздің сілтемеңіз: /start {ref[0]}")

# =================== АДМИН панелі ===================
@dp.message(F.from_user.id == ADMIN_ID)
async def admin_panel(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✏️ Видео қосу"), KeyboardButton(text="🖼 Фото қосу")],
            [KeyboardButton(text="👥 Қолданушылар санын көру")],
            [KeyboardButton(text="💰 Бонус беру")]
        ],
        resize_keyboard=True
    )
    await message.answer("🛠 Админ панелі", reply_markup=keyboard)

# =================== Видео / Фото қосу ===================
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
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            count = await cur.fetchone()
            await message.answer(f"👥 Қолданушылар саны: {count[0]}")

# =================== Бонус беру ===================
@dp.message(F.text == "💰 Бонус беру", F.from_user.id == ADMIN_ID)
async def give_bonus(message: Message):
    await message.answer("Қолданушы ID мен бонус санын жіберіңіз (мысалы: 1234567890 10):")
    dp.register_message_handler(save_bonus, F.from_user.id == ADMIN_ID, state=None)

async def save_bonus(message: Message):
    try:
        parts = message.text.split()
        user_id = int(parts[0])
        amount = int(parts[1])
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("UPDATE users SET bonus = bonus + ? WHERE id = ?", (amount, user_id))
            await db.commit()
        await message.answer(f"✅ {amount} бонус қосылды!")
    except:
        await message.answer("❌ Қате! Қолданушы ID мен санын дұрыс жіберіңіз.")

# =================== MAIN ===================
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
