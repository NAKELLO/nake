import logging
import asyncio
import sqlite3
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ContentType
from aiogram.utils.deep_linking import get_start_link
import os

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
ADMIN_IDS = [7047272652, 6927494520]
CHANNELS = ['@Qazhuboyndar', '@oqigalaruyatsiz']

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

admin_waiting_action = {}
admin_video_type = {}
media_groups = {}
VIDEO_FOLDER = "saved_videos"

if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)

def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        invited_by TEXT,
        bonus INTEGER DEFAULT 2
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id TEXT,
        type TEXT,
        file_path TEXT
    )''')
    conn.commit()
    conn.close()

def add_user(user_id, invited_by=None):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, invited_by) VALUES (?, ?)", (user_id, invited_by))
    conn.commit()
    conn.close()

def add_bonus(user_id, amount):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET bonus = bonus + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_bonus(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT bonus FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def decrease_bonus(user_id, amount):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET bonus = bonus - ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def add_video(file_id, video_type, file_path=None):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT INTO videos (file_id, type, file_path) VALUES (?, ?, ?)", (file_id, video_type, file_path))
    conn.commit()
    conn.close()

def get_random_video(video_type):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT file_id FROM videos WHERE type = ?", (video_type,))
    results = c.fetchall()
    conn.close()
    return random.choice(results)[0] if results else None

def get_video_count():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT type, COUNT(*) FROM videos GROUP BY type")
    results = c.fetchall()
    conn.close()
    return results

def get_main_keyboard(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("🛍 Магазин"))
    kb.row(KeyboardButton("🧒 Детский"), KeyboardButton("🔞 Взрослый"))
    kb.row(KeyboardButton("💎 Заработать"), KeyboardButton("🌸 PREMIUM"), KeyboardButton("💎 Баланс"))
    if user_id in ADMIN_IDS:
        kb.add(KeyboardButton("📥 Видео қосу"), KeyboardButton("📊 Статистика"))
    return kb

def get_upload_type_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🧒 Детский", callback_data="upload_kids"))
    kb.add(InlineKeyboardButton("🔞 Взрослый", callback_data="upload_adult"))
    return kb

async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = str(message.from_user.id)
    payload = message.get_args()

    add_user(user_id, payload if payload else None)

    if payload and payload != user_id:
        add_bonus(payload, 2)

    if not await check_subscription(message.from_user.id):
        channels_list = "\n".join(CHANNELS)
        return await message.answer(f"Ботты пайдалану үшін келесі каналдарға жазылыңыз:\n{channels_list}")

    await message.answer(
        "Добро пожаловать. 👋\n\nПоздравляю, ты нашёл что искал так долго.",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@dp.message_handler(lambda m: m.text == "📊 Статистика")
async def stats_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    counts = get_video_count()
    text = "📊 Видео статистикасы:\n"
    for video_type, count in counts:
        text += f"- {video_type.upper()}: {count} видео\n"
    await message.answer(text)

@dp.message_handler(lambda m: m.text in ["🧒 Детский", "🔞 Взрослый"])
async def handle_video_type(message: types.Message):
    user_id = str(message.from_user.id)
    video_type = "kids" if message.text == "🧒 Детский" else "adult"
    video = get_random_video(video_type)

    if not video:
        return await message.answer("📭 Әзірге видео жоқ. Кейінірек қайта көріңіз.")

    if message.from_user.id not in ADMIN_IDS:
        if get_bonus(user_id) < 3:
            return await message.answer("❗ 3 бонус қажет. Достарыңызды шақырыңыз.")
        decrease_bonus(user_id, 3)

    await message.answer_video(video)

@dp.message_handler(lambda m: m.text == "💎 Баланс")
async def balance_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = get_bonus(user_id)
    ref_link = await get_start_link(str(user_id), encode=True)
    await message.answer(f"💎 Сізде {bonus} бонус бар.\nДостарыңызды шақырып бонус алыңыз:\n{ref_link}")

@dp.message_handler(lambda m: m.text == "💎 Заработать")
async def earn_handler(message: types.Message):
    await balance_handler(message)

@dp.message_handler(lambda m: m.text == "🌸 PREMIUM")
async def premium_handler(message: types.Message):
    text = (
        "🌸 *PREMIUM қолжетімділік:*\n\n"
        "📆 100 бонус – 1500 ₸\n"
        "📆 200 бонус – 2000 ₸\n"
        "⏳ 1 ай шектеусіз көру – 4000 ₸\n\n"
        "💳 Төлеу үшін админге жазыңыз: @KazHubALU"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "🛍 Магазин")
async def shop_handler(message: types.Message):
    await premium_handler(message)

@dp.message_handler(lambda m: m.text == "📥 Видео қосу")
async def start_video_upload(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Қай бөлімге видео саласыз?", reply_markup=get_upload_type_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith("upload_"))
async def handle_upload_callback(callback_query: types.CallbackQuery):
    video_type = callback_query.data.replace("upload_", "")
    admin_waiting_action[callback_query.from_user.id] = True
    admin_video_type[callback_query.from_user.id] = video_type
    await callback_query.message.answer(f"🎬 {video_type.upper()} видеоларды жіберіңіз.")

@dp.message_handler(content_types=ContentType.VIDEO)
async def handle_videos(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not admin_waiting_action.get(message.from_user.id):
        return

    video_type = admin_video_type.get(message.from_user.id)
    if not video_type:
        return

    try:
        file_id = message.video.file_id
        file = await bot.get_file(file_id)
        file_path = f"{VIDEO_FOLDER}/{file_id}.mp4"
        await bot.download_file(file.file_path, file_path)
        add_video(file_id, video_type, file_path)
        await message.answer(f"✅ {video_type.upper()} видео сақталды.")
        await message.answer("🕒 Видео Telegram серверінде кем дегенде 2 апта сақталады.", parse_mode="Markdown")
        for admin_id in ADMIN_IDS:
            if admin_id != message.from_user.id:
                await bot.send_message(admin_id, f"📦 {video_type.upper()} видеосы сақталды: {file_id}")
    except Exception as e:
        await message.answer("❌ Видео жүктелмей қалды. Қайталап көріңіз.")
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, f"⚠️ Видео сақтау кезінде қате болды: {str(e)}")

    admin_waiting_action.pop(message.from_user.id, None)
    admin_video_type.pop(message.from_user.id, None)

if __name__ == '__main__':
    from aiogram import executor
    init_db()
    executor.start_polling(dp, skip_updates=True)
