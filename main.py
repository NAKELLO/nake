from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
import os
import logging

API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'
ADMIN_ID = 6927494520

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

USERS_FILE = 'users.json'
PHOTOS_FILE = 'photos.json'
VIDEOS_FILE = 'videos.json'
BONUS_FILE = 'bonus.json'

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, 'r') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# Старт
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    if user_id not in users:
        users[user_id] = {"videos": 0, "photos": 0, "invited": []}
        bonus[user_id] = 2

        if message.get_args():
            ref_id = message.get_args()
            if ref_id != user_id and ref_id in users and user_id not in users[ref_id]["invited"]:
                users[ref_id]["invited"].append(user_id)
                bonus[ref_id] += 2
                try:
                    await bot.send_message(ref_id, "🎉 Сізге 2 бонус қосылды!")
                except:
                    pass

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎥 Видео"), KeyboardButton("🖼 Фото"))
    kb.add(KeyboardButton("🎁 Бонус"))
    if message.from_user.id == ADMIN_ID:
        kb.add(KeyboardButton("👥 Қолданушылар саны"), KeyboardButton("📢 Хабарлама жіберу"))
    await message.answer("Қош келдіңіз!", reply_markup=kb)

# Фото жіберу (тек админ)
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    photos = load_json(PHOTOS_FILE)
    photo_id = message.photo[-1].file_id
    photos.setdefault("all", []).append(photo_id)
    save_json(PHOTOS_FILE, photos)
    await message.reply("✅ Фото сақталды.")

# Видео жіберу (тек админ)
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_video(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    videos = load_json(VIDEOS_FILE)
    video_id = message.video.file_id
    videos.setdefault("all", []).append(video_id)
    save_json(VIDEOS_FILE, videos)
    await message.reply("✅ Видео сақталды.")

# Видео көру
@dp.message_handler(lambda m: m.text == "🎥 Видео")
async def send_video(message: types.Message):
    user_id = str(message.from_user.id)
    videos = load_json(VIDEOS_FILE)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    video_list = videos.get("all", [])
    index = users[user_id]["videos"] % len(video_list) if video_list else 0

    if bonus.get(user_id, 0) >= 3 and video_list:
        await bot.send_video(message.chat.id, video_list[index])
        users[user_id]["videos"] += 1
        bonus[user_id] -= 3
    elif not video_list:
        await message.answer("📭 Видео жоқ.")
    else:
        await message.answer("❗️ Бонус жетіспейді.")

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

# Фото көру
@dp.message_handler(lambda m: m.text == "🖼 Фото")
async def send_photo(message: types.Message):
    user_id = str(message.from_user.id)
    photos = load_json(PHOTOS_FILE)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    photo_list = photos.get("all", [])
    index = users[user_id]["photos"] % len(photo_list) if photo_list else 0

    if bonus.get(user_id, 0) >= 4 and photo_list:
        await bot.send_photo(message.chat.id, photo_list[index])
        users[user_id]["photos"] += 1
        bonus[user_id] -= 4
    elif not photo_list:
        await message.answer("📭 Фото жоқ.")
    else:
        await message.answer("❗️ Бонус жетіспейді.")

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

# Бонус
@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_check(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    invited = users.get(user_id, {}).get("invited", [])
    ref_link = f"https://t.me/{(await bot.get_me()).username}?start={user_id}"
    await message.answer(
        f"🎁 Бонус: {bonus.get(user_id, 0)}\n"
        f"👥 Шақырғандар: {len(invited)}\n"
        f"🔗 Реф. сілтеме: {ref_link}"
    )

# Қолданушылар саны
@dp.message_handler(lambda m: m.text == "👥 Қолданушылар саны")
async def user_count(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_json(USERS_FILE)
    await message.answer(f"👥 Жалпы қолданушы: {len(users)}")

# Хабарлама тарату
@dp.message_handler(lambda m: m.text == "📢 Хабарлама жіберу")
async def ask_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("✏️ Хабарламаны жазыңыз:")
    dp.register_message_handler(broadcast_msg, content_types=types.ContentType.TEXT, state=None)

async def broadcast_msg(message: types.Message):
    users = load_json(USERS_FILE)
    for user_id in users:
        try:
            await bot.send_message(user_id, message.text)
        except:
            continue
    await message.answer("✅ Хабарлама жіберілді.")
    dp.message_handlers.unregister(broadcast_msg)

# Іске қосу
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
