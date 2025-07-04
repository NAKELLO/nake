from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json, os, logging

API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'
ADMIN_ID = 6927494520
CHANNELS = ['@Gey_Angime', '@Qazhuboyndar']

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'
PHOTOS_FILE = 'photos.json'
VIDEOS_FILE = 'videos.json'

# ---------------------- JSON Functions ----------------------
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

# ---------------------- Start Command ----------------------
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
            if ref_id != user_id and ref_id in users and user_id not in users[ref_id]['invited']:
                users[ref_id]['invited'].append(user_id)
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
        kb.add(KeyboardButton("📢 Хабарлама жіберу"), KeyboardButton("👥 Қолданушылар саны"))

    await message.answer("Қош келдіңіз!", reply_markup=kb)

# ---------------------- Handlers ----------------------
@dp.message_handler(lambda m: m.text == "🎥 Видео")
async def video_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    videos = load_json(VIDEOS_FILE).get("all", [])

    if bonus.get(user_id, 0) >= 3 and videos:
        index = users[user_id]["videos"] % len(videos)
        await message.answer_video(videos[index])
        users[user_id]["videos"] += 1
        bonus[user_id] -= 3
    elif not videos:
        await message.answer("📛 Видео жоқ.")
    else:
        await message.answer("❌ 3 бонус қажет. Реферал арқылы жинаңыз.")

    save_json(BONUS_FILE, bonus)
    save_json(USERS_FILE, users)

@dp.message_handler(lambda m: m.text == "🖼 Фото")
async def photo_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    photos = load_json(PHOTOS_FILE).get("all", [])

    if bonus.get(user_id, 0) >= 4 and photos:
        index = users[user_id]["photos"] % len(photos)
        await message.answer_photo(photos[index])
        users[user_id]["photos"] += 1
        bonus[user_id] -= 4
    elif not photos:
        await message.answer("📛 Фото жоқ.")
    else:
        await message.answer("❌ 4 бонус қажет. Реферал арқылы жинаңыз.")

    save_json(BONUS_FILE, bonus)
    save_json(USERS_FILE, users)

@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    ref = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
    await message.answer(f"🎁 Бонус: {bonus.get(user_id, 0)}\n👥 Шақырғандар саны: {len(users[user_id]['invited'])}\n🔗 Сілтеме: {ref}")

@dp.message_handler(lambda m: m.text == "👥 Қолданушылар саны")
async def user_count(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        users = load_json(USERS_FILE)
        await message.answer(f"👥 Қолданушылар саны: {len(users)}")

@dp.message_handler(lambda m: m.text == "📢 Хабарлама жіберу")
async def broadcast_prompt(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("✉️ Хабарламаны жазыңыз:")
        dp.register_message_handler(send_broadcast, content_types=types.ContentTypes.TEXT, state=None)

async def send_broadcast(message: types.Message):
    users = load_json(USERS_FILE)
    for user_id in users:
        try:
            await bot.send_message(user_id, message.text)
        except:
            continue
    await message.answer("✅ Хабарлама жіберілді!")

@dp.message_handler(content_types=['photo'])
async def save_photo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    photos = load_json(PHOTOS_FILE)
    photo_id = message.photo[-1].file_id
    photos.setdefault("all", []).append(photo_id)
    save_json(PHOTOS_FILE, photos)
    await message.answer("✅ Фото сақталды.")

@dp.message_handler(content_types=['video'])
async def save_video(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    videos = load_json(VIDEOS_FILE)
    video_id = message.video.file_id
    videos.setdefault("all", []).append(video_id)
    save_json(VIDEOS_FILE, videos)
    await message.answer("✅ Видео сақталды.")

# ---------------------- Start Bot ----------------------
if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    executor.start_polling(dp, skip_updates=True)
