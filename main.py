import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ChatMemberStatus

# =================== Параметрлер ===================
API_TOKEN = "8757577500:AAG7FNMvw54vsg9s343MB-DDCU9kOPS-Esk"   # Сенің бот токенің
ADMIN_ID = 6303091468                                          # Сенің Telegram ID
CHANNEL_USERNAME = "@kazakcombots"                               # Сенің канал username
BOT_USERNAME = "@kazakcombot"                                   # Сенің бот username
# ======================================================

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)

# =================== FSM ===================
class AdminStates(StatesGroup):
    waiting_video = State()
    waiting_photo = State()
    giving_bonus = State()

# =================== DATABASE ===================
async def init_db():
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                bonus INTEGER DEFAULT 0,
                ref TEXT DEFAULT ''
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

# =================== Бастау командасы ===================
@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    args = message.get_args()  # реферал параметрі
    async with aiosqlite.connect("bot_database.db") as db:
        # Қолданушыны қосу
        await db.execute("INSERT OR IGNORE INTO users (id, bonus) VALUES (?, ?)", (user_id, 2))
        # Егер реферал болса
        if args:
            ref_id = int(args)
            await db.execute("UPDATE users SET bonus = bonus + 6 WHERE id = ?", (ref_id,))
        await db.commit()

    is_subscribed = await check_subscription(user_id)
    if not is_subscribed:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton("📢 Каналга жазылу")],[KeyboardButton("✅ Тексеру")]],
            resize_keyboard=True
        )
        await message.answer("❗ Ботты қолдану үшін каналға тіркелу керек.", reply_markup=keyboard)
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton("📸 Фото көру"), KeyboardButton("🎥 Видео көру")]],
            resize_keyboard=True
        )
        await message.answer("✅ Қош келдің! Бот жұмыс істеп тұр 🚀", reply_markup=keyboard)

# =================== Тексеру батырмасы ===================
@dp.message(Text("✅ Тексеру"))
async def check_sub_handler(message: Message):
    user_id = message.from_user.id
    if await check_subscription(user_id):
        await message.answer("✅ Рақмет! Енді ботты қолдана аласыз.")
    else:
        await message.answer("❌ Әлі тіркелмегенсің! Каналга жазылып, қайта тексер.")

# =================== Фото / Видео батырмалары ===================
@dp.message(Text("🎥 Видео көру"))
async def show_videos(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT bonus FROM users WHERE id=?", (user_id,)) as cursor:
            user_bonus = await cursor.fetchone()
            if not user_bonus or user_bonus[0] < 3:
                await message.answer("❌ Бонус жетіспейді. Реферал арқылы бонус жина!")
                return
        # Кезекпен видео алу
        async with db.execute("SELECT file FROM videos ORDER BY id ASC") as cursor:
            videos = await cursor.fetchall()
            if videos:
                for video in videos:
                    await message.answer(video[0])
                # Бонус азайту
                await db.execute("UPDATE users SET bonus = bonus - 3 WHERE id=?", (user_id,))
                await db.commit()
            else:
                await message.answer("Видео әлі қосылмаған.")

@dp.message(Text("📸 Фото көру"))
async def show_photos(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT bonus FROM users WHERE id=?", (user_id,)) as cursor:
            user_bonus = await cursor.fetchone()
            if not user_bonus or user_bonus[0] < 1:
                await message.answer("❌ Бонус жетіспейді. Реферал арқылы бонус жина!")
                return
        # Кезекпен фото алу
        async with db.execute("SELECT file FROM photos ORDER BY id ASC") as cursor:
            photos = await cursor.fetchall()
            if photos:
                for photo in photos:
                    await message.answer(photo[0])
                # Бонус азайту
                await db.execute("UPDATE users SET bonus = bonus - 1 WHERE id=?", (user_id,))
                await db.commit()
            else:
                await message.answer("Фото әлі қосылмаған.")

# =================== Админ панелі ===================
@dp.message(Text("/admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Сен админ емессің!")
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("✏️ Видео қосу", callback_data="admin_add_video")],
            [InlineKeyboardButton("🖼 Фото қосу", callback_data="admin_add_photo")],
            [InlineKeyboardButton("👥 Қолданушылар санын көру", callback_data="admin_user_count")],
            [InlineKeyboardButton("💎 Бонус беру", callback_data="admin_give_bonus")]
        ]
    )
    await message.answer("🛠 Админ панелі", reply_markup=keyboard)

# =================== Админ callback-тары ===================
@dp.callback_query(F.data.startswith("admin_"))
async def admin_callbacks(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Сен админ емессің!", show_alert=True)
        return

    if data == "admin_add_video":
        await callback.message.answer("Видео сілтемесін жіберіңіз:")
        await state.set_state(AdminStates.waiting_video)
    elif data == "admin_add_photo":
        await callback.message.answer("Фото сілтемесін жіберіңіз:")
        await state.set_state(AdminStates.waiting_photo)
    elif data == "admin_user_count":
        async with aiosqlite.connect("bot_database.db") as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                count = await cursor.fetchone()
                await callback.message.answer(f"👥 Қолданушылар саны: {count[0]}")
    elif data == "admin_give_bonus":
        await callback.message.answer("Кімге бонус бересіз (user_id енгізіңіз):")
        await state.set_state(AdminStates.giving_bonus)

# =================== Админ FSM ===================
@dp.message(AdminStates.waiting_video, F.from_user.id == ADMIN_ID)
async def save_video(message: Message, state: FSMContext):
    video_url = message.text
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT INTO videos (file) VALUES (?)", (video_url,))
        await db.commit()
    await message.answer("✅ Видео қосылды!")
    await state.clear()

@dp.message(AdminStates.waiting_photo, F.from_user.id == ADMIN_ID)
async def save_photo(message: Message, state: FSMContext):
    photo_url = message.text
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT INTO photos (file) VALUES (?)", (photo_url,))
        await db.commit()
    await message.answer("✅ Фото қосылды!")
    await state.clear()

@dp.message(AdminStates.giving_bonus, F.from_user.id == ADMIN_ID)
async def give_bonus(message: Message, state: FSMContext):
    try:
        parts = message.text.split()
        user_id = int(parts[0])
        amount = int(parts[1])
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("UPDATE users SET bonus = bonus + ? WHERE id=?", (amount, user_id))
            await db.commit()
        await message.answer(f"✅ {user_id} пайдаланушыға {amount} бонус берілді!")
    except:
        await message.answer("❌ Қате! Формат: user_id amount")
    await state.clear()

# =================== MAIN ===================
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
