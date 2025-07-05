from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json, os, logging

API_TOKEN = 'токеніңді мында қой'
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
    if not os.path.exists(file):
        if file in [PHOTOS_FILE, VIDEOS_FILE, KIDS_VIDEOS_FILE]:
            return {"all": []}
        return {}
    with open(file, 'r') as f:
        try:
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

    bad_keywords = ['police', 'gov', 'депутат', 'суд', 'прокуратура', 'din', 'mzrk', 'minjust']
    username = (message.from_user.username or '').lower()
    fullname = (message.from_user.full_name or '').lower()
    for word in bad_keywords:
        if word in username or word in fullname:
            return

    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    if user_id not in users:
        if not await check_subscription(message.from_user.id):
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

@dp.message_handler(lambda m: m.text == "🎥 Видео")
async def video_handler(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)
    videos = load_json(VIDEOS_FILE).get("all", [])

    if not videos:
        await message.answer("⚠️ Видео табылмады.")
        return

    if message.from_user.id != ADMIN_ID and bonus.get(user_id, 0) < 3:
        await message.answer("❌ Видео көру үшін 3 бонус қажет.")
        return

    index = users[user_id]["videos"] % len(videos)
    await message.answer_video(videos[index])
    users[user_id]["videos"] += 1
    if message.from_user.id != ADMIN_ID:
        bonus[user_id] -= 3

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

@dp.message_handler(lambda m: m.text == "🖼 Фото")
async def photo_handler(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)
    photos = load_json(PHOTOS_FILE).get("all", [])

    if not photos:
        await message.answer("⚠️ Фото табылмады.")
        return

    if message.from_user.id != ADMIN_ID and bonus.get(user_id, 0) < 4:
        await message.answer("❌ Фото көру үшін 4 бонус қажет.")
        return

    index = users[user_id]["photos"] % len(photos)
    await message.answer_photo(photos[index])
    users[user_id]["photos"] += 1
    if message.from_user.id != ADMIN_ID:
        bonus[user_id] -= 4

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

@dp.message_handler(lambda m: m.text == "👶 Детский")
async def kids_handler(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)
    kids = load_json(KIDS_VIDEOS_FILE).get("all", [])

    if not kids:
        await message.answer("⚠️ Детский видеолар жоқ.")
        return

    if message.from_user.id != ADMIN_ID and bonus.get(user_id, 0) < 6:
        await message.answer("❌ Детский видео үшін 6 бонус қажет.")
        return

    index = users[user_id]["kids"] % len(kids)
    await message.answer_video(kids[index])
    users[user_id]["kids"] += 1
    if message.from_user.id != ADMIN_ID:
        bonus[user_id] -= 6

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    ref = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await message.answer(f"🎁 Бонус: {bonus.get(user_id, 0)}\n👥 Шақырғандар саны: {len(users[user_id]['invited'])}\n🔗 Сілтеме: {ref}")

@dp.message_handler(content_types=['video'])
async def save_video(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    videos = load_json(VIDEOS_FILE)
    videos.setdefault("all", []).append(message.video.file_id)
    save_json(VIDEOS_FILE, videos)
    await message.answer("✅ Видео сақталды.")

@dp.message_handler(content_types=['photo'])
async def save_photo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    photos = load_json(PHOTOS_FILE)
    photos.setdefault("all", []).append(message.photo[-1].file_id)
    save_json(PHOTOS_FILE, photos)
    await message.answer("✅ Фото сақталды.")

@dp.message_handler(lambda m: m.text == "👥 Қолданушылар саны")
async def count_users(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        users = load_json(USERS_FILE)
        await message.answer(f"👥 Қолданушылар саны: {len(users)}")

if __name__ == '__main__':
    print("✅ Бот іске қосылды!")
    executor.start_polling(dp, skip_updates=True)
