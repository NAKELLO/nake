import os
import json
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
ADMIN_IDS = [7702280273]  # Өз Telegram ID-ні қой
CHANNELS = ["@oqigalaruyatsiz", "@Qazhuboyndar"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# 🎮 Бонусты басқару
BONUS_FILE = 'bonus.json'
if not os.path.exists(BONUS_FILE):
    with open(BONUS_FILE, 'w') as f:
        json.dump({}, f)

def load_bonus():
    with open(BONUS_FILE, 'r') as f:
        return json.load(f)

def save_bonus(bonus):
    with open(BONUS_FILE, 'w') as f:
        json.dump(bonus, f)

def get_bonus(user_id):
    bonus = load_bonus()
    return bonus.get(str(user_id), 2)

def update_bonus(user_id, amount):
    bonus = load_bonus()
    bonus[str(user_id)] = bonus.get(str(user_id), 2) + amount
    save_bonus(bonus)

# 📊 SQLite БД
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)""")
conn.commit()

# ⌨️ Түймелер
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add("▶️ Смотреть", "🔥 Жанр")
main_kb.add("🛍 Магазин", "💎 Заработать")
main_kb.add("🌸 PREMIUM", "💎 Баланс")

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add("📥 Видео жүктеу (дет)", "📥 Видео жүктеу (взр)")
admin_kb.add("📊 Статистика", "📣 Рассылка")

# 📦 /start
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    user_id = msg.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    conn.commit()
    update_bonus(user_id, 0)  # тіркелсе — бонус тексеру
    ref = msg.get_args()
    if ref and ref.isdigit() and int(ref) != user_id:
        ref_id = int(ref)
        # Каналдарға тіркелгенін тексер
        joined = True
        for channel in CHANNELS:
            try:
                member = await bot.get_chat_member(channel, user_id)
                if member.status not in ['member', 'creator', 'administrator']:
                    joined = False
            except:
                joined = False
        if joined:
            update_bonus(ref_id, 2)
            await bot.send_message(ref_id, f"🎉 Сізге 2 бонус түсті! Реферал шақырғаныңыз үшін.")
    await msg.answer("Қош келдің! Түймелерді пайдаланыңыз:", reply_markup=main_kb)

# ▶️ Смотреть
@dp.message_handler(lambda msg: msg.text == "▶️ Смотреть")
async def watch_video(msg: types.Message):
    user_id = msg.from_user.id
    if get_bonus(user_id) >= 3:
        update_bonus(user_id, -3)
        await msg.answer_video(open("videos/detskiy.mp4", "rb"), caption="🎥 Детский видео")
    else:
        await msg.answer("❌ Бонус жетіспейді. '💎 Заработать' арқылы бонус алыңыз.")

# 🔥 Жанр
@dp.message_handler(lambda msg: msg.text == "🔥 Жанр")
async def genre(msg: types.Message):
    await msg.answer("Қазір тек бір жанр бар: Детский видео. Көбірек қосылады.")

# 🛍 Магазин
@dp.message_handler(lambda msg: msg.text == "🛍 Магазин")
async def shop(msg: types.Message):
    await msg.answer("💰 Бонустар сатып алу:\n\n50 бонус = 2000тг\n100 бонус = 4000тг\n\nКупить: @KazHubALU")

# 💎 Заработать
@dp.message_handler(lambda msg: msg.text == "💎 Заработать")
async def earn_bonus(msg: types.Message):
    user_id = msg.from_user.id
    ref_link = f"https://t.me/Darvinuyatszdaribot?start={user_id}"
    await msg.answer(f"👥 Дос шақырыңыз да бонус алыңыз!\nӘр тіркелген адам үшін 2 бонус.\n\nРеферал ссылкаңыз:\n{ref_link}")

# 💎 Баланс
@dp.message_handler(lambda msg: msg.text == "💎 Баланс")
async def balance(msg: types.Message):
    bonus = get_bonus(msg.from_user.id)
    await msg.answer(f"💎 Сіздің бонусыңыз: {bonus}")

# 🌸 PREMIUM
@dp.message_handler(lambda msg: msg.text == "🌸 PREMIUM")
async def premium(msg: types.Message):
    await msg.answer("👑 VIP жазылым алу үшін: @KazHubALU")

# 👑 Админ панелі
@dp.message_handler(lambda msg: msg.from_user.id in ADMIN_IDS and msg.text == "/admin")
async def admin_panel(msg: types.Message):
    await msg.answer("🛠 Админ панелі:", reply_markup=admin_kb)

# 📥 Видео жүктеу
@dp.message_handler(lambda msg: msg.from_user.id in ADMIN_IDS and msg.text.startswith("📥"))
async def upload_video(msg: types.Message):
    await msg.answer("🎥 Видео жіберіңіз...")

@dp.message_handler(lambda msg: msg.from_user.id in ADMIN_IDS, content_types=types.ContentType.VIDEO)
async def save_admin_video(msg: types.Message):
    if "дет" in msg.caption.lower():
        path = "videos/detskiy.mp4"
    elif "взр" in msg.caption.lower():
        path = "videos/vzroslyy.mp4"
    else:
        return await msg.answer("❗ Видеоны жіберу үшін тақырып (дет / взр) жазыңыз.")
    await msg.video.download(destination_file=path)
    await msg.answer("✅ Видео сақталды!")

# 📊 Статистика
@dp.message_handler(lambda msg: msg.from_user.id in ADMIN_IDS and msg.text == "📊 Статистика")
async def stats(msg: types.Message):
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    await msg.answer(f"📈 Жалпы қолданушылар: {count}")

# 📣 Рассылка
broadcast_mode = {}

@dp.message_handler(lambda msg: msg.from_user.id in ADMIN_IDS and msg.text == "📣 Рассылка")
async def broadcast_start(msg: types.Message):
    broadcast_mode[msg.from_user.id] = True
    await msg.answer("✉️ Хабарлама жіберіңіз:")

@dp.message_handler(lambda msg: broadcast_mode.get(msg.from_user.id))
async def do_broadcast(msg: types.Message):
    broadcast_mode[msg.from_user.id] = False
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    count = 0
    for (uid,) in users:
        try:
            await bot.send_message(uid, msg.text)
            count += 1
        except:
            pass
    await msg.answer(f"✅ Жіберілді: {count} адамға.")

# 🟢 Запуск
if __name__ == "__main__":
    if not os.path.exists("videos"):
        os.mkdir("videos")
    executor.start_polling(dp, skip_updates=True)

