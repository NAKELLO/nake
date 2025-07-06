import asyncio
import logging
import json
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = 'YOUR_API_TOKEN_HERE'  # Токеніңізді енгізіңіз
ADMIN_ID = 6927494520  # Админ ID
BOT_USERNAME = 'Darvinuyatszdaribot'  # Боттың юзернеймі

# Файлдар
USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'
KIDS_VIDEOS_FILE = 'kids_videos.json'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def load_json(file):
    if not os.path.exists(file):
        return {"all": []} if 'videos' in file else {}
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    if user_id not in users:
        users[user_id] = {"videos": 0, "photos": 0, "kids": 0, "invited": []}
        bonus[user_id] = 2  # Жаңа қолданушыға 2 бонус
        save_json(USERS_FILE, users)
        save_json(BONUS_FILE, bonus)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("👶 Детский"), KeyboardButton("🎁 Бонус"))
    kb.add(KeyboardButton("💎 VIP қолжетімділік"))

    await message.answer("Қош келдіңіз!", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "👶 Детский")
async def kids_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    kids_videos = load_json(KIDS_VIDEOS_FILE).get("all", [])

    if not kids_videos:
        await message.answer("⚠️ Детский видеолар жоқ.")
        return

    if message.from_user.id != ADMIN_ID and bonus.get(user_id, 0) < 6:
        await message.answer("❌ Бұл бөлімді көру үшін 6 бонус қажет.")
        return

    index = users[user_id]["kids"] % len(kids_videos)
    await message.answer_video(kids_videos[index])
    users[user_id]["kids"] += 1
    if message.from_user.id != ADMIN_ID:
        bonus[user_id] -= 6
    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

@dp.message_handler(content_types=types.ContentType.VIDEO)
async def save_kids_video(message: types.Message):
    if message.chat.id != ADMIN_ID:
        return

    data = load_json(KIDS_VIDEOS_FILE)
    file_id = message.video.file_id

    if file_id not in data['all']:
        data['all'].append(file_id)
        save_json(KIDS_VIDEOS_FILE, data)
        await message.reply("✅ Детский видео сақталды.")
    else:
        await message.reply("ℹ️ Бұл видео бұрыннан бар.")

if __name__ == '__main__':
    try:
        print("🤖 Бот іске қосылды!")
        from aiogram import executor
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        logging.error(f"Error starting the bot: {e}")
