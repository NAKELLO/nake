import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

# =================== Параметрлер ===================
API_TOKEN = "8757577500:AAG7FNMvw54vsg9s343MB-DDCU9kOPS-Esk"
ADMIN_ID = 6303091468
CHANNEL_USERNAME = "@kazakcombots"
BOT_USERNAME = "@kazakcombot"
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
                bonus INTEGER DEFAULT 2,
                referrer_id INTEGER,
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
# ================================================

# =================== Каналға тіркелу ===================
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

# =================== Бастау командасы ===================
@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    args = message.get_args()
    ref_id = int(args) if args.isdigit() else None

    async with aiosqlite.connect("bot_database.db") as db:
        # Жаңа қолданушыны қосу
        await db.execute("""
            INSERT OR IGNORE INTO users (id, referrer_id)
            VALUES (?, ?)
        """, (user_id, ref_id))
        # Егер шақырған адам болса, бонус қосу
        if ref_id:
            await db.execute("""
                UPDATE users
                SET bonus = bonus + 6, referral_count = referral_count + 1
                WHERE id = ?
            """, (ref_id,))
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
        await message.answer(
            f"❗ Ботты қолдану үшін каналға тіркелу керек.\nРеферал сілтеме: t.me/{BOT_USERNAME}?start={user_id}",
            reply_markup=keyboard
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📸 Фото көру"), KeyboardButton(text="🎥 Видео көру")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"✅ Қош келдің! Бот жұмыс істеп тұр 🚀\nРеферал сілтеме: t.me/{BOT_USERNAME}?start={user_id}",
            reply_markup=keyboard
        )

# =================== Тексеру батырмасы ===================
@dp.message(F.text == "✅ Тексеру")
async def check_sub_handler(message: Message):
    user_id = message.from_user.id
    is_subscribed = await check_subscription(user_id)
    if is_subscribed:
        await message.answer("✅ Рақмет! Енді ботты қолдана аласыз.")
    else:
        await message.answer("❌ Әлі тіркелмегенсің! Каналга жазылып, қайта тексер.")

# =================== Видео / Фото батырмалары ===================
@dp.message(F.text == "🎥 Видео көру")
async def show_videos(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT bonus FROM users WHERE id = ?", (user_id,)) as cur:
            bonus = await cur.fetchone()
            if not bonus or bonus[0] < 3:
                await message.answer("❌ Бонус жетіспейді! Дос шақырып бонус жинаңыз.")
                return
            # 3 бонус шегеру
            await db.execute("UPDATE users SET bonus = bonus - 3 WHERE id = ?", (user_id,))
            # Алма кезекпен видео шығару
            async with db.execute("SELECT file FROM videos ORDER BY id") as cursor:
                videos = await cursor.fetchall()
                if videos:
                    await message.answer(videos[0][0])
                else:
                    await message.answer("Видео әлі жоқ.")

        await db.commit()

@dp.message(F.text == "📸 Фото көру")
async def show_photos(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT bonus FROM users WHERE id = ?", (user_id,)) as cur:
            bonus = await cur.fetchone()
            if not bonus or bonus[0] < 3:
                await message.answer("❌ Бонус жетіспейді! Дос шақырып бонус жинаңыз.")
                return
            await db.execute("UPDATE users SET bonus = bonus - 3 WHERE id = ?", (user_id,))
            async with db.execute("SELECT file FROM photos ORDER BY id") as cursor:
                photos = await cursor.fetchall()
                if photos:
                    await message.answer(photos[0][0])
                else:
                    await message.answer("Фото әлі жоқ.")
        await db.commit()

# =================== Админ панелі ===================
@dp.message(F.from_user.id == ADMIN_ID)
async def admin_panel(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✏️ Видео қосу"), KeyboardButton(text="🖼 Фото қосу")],
            [KeyboardButton(text="👥 Қолданушылар санын көру")],
            [KeyboardButton(text="💎 Бонус беру")]
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
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            count = await cur.fetchone()
            await message.answer(f"👥 Қолданушылар саны: {count[0]}")

# =================== Бонус беру ===================
@dp.message(F.text == "💎 Бонус беру", F.from_user.id == ADMIN_ID)
async def give_bonus(message: Message):
    await message.answer("Бонус қосу үшін қолданушының ID-ын жіберіңіз:")
    dp.register_message_handler(send_bonus, F.from_user.id == ADMIN_ID, state=None)

async def send_bonus(message: Message):
    try:
        user_id, bonus_amount = map(int, message.text.split())
    except:
        await message.answer("Қате! Пішімі: <user_id> <bonus_amount>")
        return
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("UPDATE users SET bonus = bonus + ? WHERE id = ?", (bonus_amount, user_id))
        await db.commit()
    await message.answer(f"✅ {bonus_amount} бонус {user_id} қолданушысына қосылды!")

# =================== MAIN ===================
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
