from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json, os, logging

API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'
ADMIN_ID = 6927494520
BOT_USERNAME = 'Darvinuyatszdaribot'

CHANNELS = ['@Gey_Angime', '@Qazhuboyndar', '@oqigalaruyatsiz']

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'
PHOTOS_FILE = 'photos.json'
VIDEOS_FILE = 'videos.json'
KIDS_VIDEOS_FILE = 'kids_videos.json'

def load_json(file):
    try:
        if not os.path.exists(file):
            if file in [PHOTOS_FILE, VIDEOS_FILE, KIDS_VIDEOS_FILE]:
                return {"all": []}
            return {}
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {"all": []} if file in [PHOTOS_FILE, VIDEOS_FILE, KIDS_VIDEOS_FILE] else {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type != 'private':
        return

    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    if user_id not in users:
        is_subscribed = await check_subscription(message.from_user.id)
        if not is_subscribed:
            links = "\n".join([f"👉 {c}" for c in CHANNELS])
            await message.answer(f"📛 Ботты қолдану үшін келесі арналарға тіркеліңіз:\n\n{links}\n\n✅ Тіркелген соң /start деп қайта жазыңыз.")
            return

        users[user_id] = {"videos": 0, "photos": 0, "kids": 0, "invited": []}
        bonus[user_id] = 2

        if message.get_args():
            ref_id = message.get_args()
            if ref_id != user_id and ref_id in users and user_id not in users[ref_id]['invited']:
                users[ref_id]['invited'].append(user_id)
                bonus[ref_id] += 2
                try:
                    await bot.send_message(int(ref_id), "🎉 Сізге 2 бонус қосылды!")
                except:
                    pass

        save_json(USERS_FILE, users)
        save_json(BONUS_FILE, bonus)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎥 Видео"), KeyboardButton("🖼 Фото"))
    kb.add(KeyboardButton("👶 Детский"), KeyboardButton("🎁 Бонус"))
    if message.from_user.id == ADMIN_ID:
        kb.add(KeyboardButton("📢 Хабарлама жіберу"), KeyboardButton("👥 Қолданушылар саны"))

    await message.answer("Қош келдіңіз!", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    ref = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await message.answer(f"🎁 Сізде {bonus.get(user_id, 0)} бонус бар.\n🔗 Сілтеме: {ref}\n👥 Шақырғандар саны: {len(users[user_id]['invited'])}")

@dp.message_handler(lambda m: m.text == "🎥 Видео")
async def video_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    videos = load_json(VIDEOS_FILE).get("all", [])

    if not videos:
        await message.answer("⚠️ Видео табылмады.")
        return

    if bonus.get(user_id, 0) < 3:
        await message.answer("❌ Видео көру үшін 3 бонус қажет. Реферал арқылы жинаңыз.")
        return

    index = users[user_id]["videos"] % len(videos)
    await message.answer_video(videos[index])
    users[user_id]["videos"] += 1
    bonus[user_id] -= 3
    save_json(VIDEOS_FILE, {"all": videos})
    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

@dp.message_handler(lambda m: m.text == "🖼 Фото")
async def photo_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    photos = load_json(PHOTOS_FILE).get("all", [])

    if not photos:
        await message.answer("⚠️ Фото табылмады.")
        return

    if bonus.get(user_id, 0) < 4:
        await message.answer("❌ Фото көру үшін 4 бонус қажет. Реферал арқылы жинаңыз.")
        return

    index = users[user_id]["photos"] % len(photos)
    await message.answer_photo(photos[index])
    users[user_id]["photos"] += 1
    bonus[user_id] -= 4
    save_json(PHOTOS_FILE, {"all": photos})
    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

@dp.message_handler(lambda m: m.text == "👶 Детский")
async def kids_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    kids_videos = load_json(KIDS_VIDEOS_FILE).get("all", [])

    if not kids_videos:
        await message.answer("⚠️ Детский видеолар жоқ.")
        return

    if bonus.get(user_id, 0) < 6:
        await message.answer("❌ Бұл бөлімді көру үшін 6 бонус қажет. Реферал арқылы жинаңыз.")
        return

    index = users[user_id]["kids"] % len(kids_videos)
    await message.answer_video(kids_videos[index])
    users[user_id]["kids"] += 1
    bonus[user_id] -= 6
    save_json(KIDS_VIDEOS_FILE, {"all": kids_videos})
    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    executor.start_polling(dp, skip_updates=True)
