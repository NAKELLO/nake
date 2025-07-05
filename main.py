from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json, os, logging

API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'
ADMIN_ID = 6927494520
BOT_USERNAME = 'Darvinuyatszdaribot'

CHANNELS = ['@Gey_Angime', '@Qazhuboyndar']

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'
PHOTOS_FILE = 'photos.json'
VIDEOS_FILE = 'videos.json'
KIDS_VIDEOS_FILE = 'kids_videos.json'

admin_waiting_broadcast = {}

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
                    await bot.send_message(ref_id, "🎉 Сізге 2 бонус қосылды!")
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

@dp.message_handler(lambda m: m.chat.type == 'private' and m.text == "🎥 Видео")
async def video_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    videos = load_json(VIDEOS_FILE).get("all", [])

    if message.from_user.id != ADMIN_ID and bonus.get(user_id, 0) < 3:
        await message.answer("❌ Видео көру үшін 3 бонус қажет. Реферал арқылы жинаңыз.")
        return

    if not videos:
        await message.answer("⚠️ Видео табылмады.")
        return

    index = users[user_id]["videos"] % len(videos)
    await message.answer_video(videos[index])
    users[user_id]["videos"] += 1
    if message.from_user.id != ADMIN_ID:
        bonus[user_id] -= 3

    save_json(BONUS_FILE, bonus)
    save_json(USERS_FILE, users)

@dp.message_handler(lambda m: m.chat.type == 'private' and m.text == "🖼 Фото")
async def photo_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    photos = load_json(PHOTOS_FILE).get("all", [])

    if message.from_user.id != ADMIN_ID and bonus.get(user_id, 0) < 4:
        await message.answer("❌ Фото көру үшін 4 бонус қажет. Реферал арқылы жинаңыз.")
        return

    if not photos:
        await message.answer("⚠️ Фото табылмады.")
        return

    index = users[user_id]["photos"] % len(photos)
    await message.answer_photo(photos[index])
    users[user_id]["photos"] += 1
    if message.from_user.id != ADMIN_ID:
        bonus[user_id] -= 4

    save_json(BONUS_FILE, bonus)
    save_json(USERS_FILE, users)

@dp.message_handler(lambda m: m.chat.type == 'private' and m.text == "👶 Детский")
async def kids_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    kids_videos = load_json(KIDS_VIDEOS_FILE).get("all", [])

    if message.from_user.id != ADMIN_ID and bonus.get(user_id, 0) < 3:
        await message.answer("❌ Детский видео көру үшін 3 бонус қажет. Реферал арқылы жинаңыз.")
        return

    if not kids_videos:
        await message.answer("⚠️ Детский видео табылмады.")
        return

    index = users[user_id]["kids"] % len(kids_videos)
    await message.answer_video(kids_videos[index])
    users[user_id]["kids"] += 1
    if message.from_user.id != ADMIN_ID:
        bonus[user_id] -= 3

    save_json(BONUS_FILE, bonus)
    save_json(USERS_FILE, users)

@dp.message_handler(lambda m: m.chat.type == 'private' and m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    if user_id not in users:
        await message.answer("Алдымен /start командасын басыңыз.")
        return
    ref = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await message.answer(f"🎁 Бонус: {bonus.get(user_id, 0)}\n👥 Шақырғандар саны: {len(users[user_id]['invited'])}\n🔗 Сілтеме: {ref}")

@dp.message_handler(lambda m: m.chat.type == 'private' and m.text == "👥 Қолданушылар саны")
async def user_count(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        users = load_json(USERS_FILE)
        await message.answer(f"👥 Қолданушылар саны: {len(users)}")

@dp.message_handler(lambda m: m.chat.type == 'private' and m.text == "📢 Хабарлама жіберу")
async def broadcast_prompt(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        admin_waiting_broadcast[message.from_user.id] = True
        await message.answer("✉️ Хабарламаны жазыңыз:")

@dp.message_handler(lambda m: m.chat.type == 'private')
async def send_broadcast(message: types.Message):
    if message.from_user.id == ADMIN_ID and admin_waiting_broadcast.get(message.from_user.id):
        users = load_json(USERS_FILE)
        for user_id in users:
            try:
                await bot.send_message(user_id, message.text)
            except:
                continue
        await message.answer("✅ Хабарлама жіберілді!")
        admin_waiting_broadcast[message.from_user.id] = False

@dp.message_handler(content_types=['photo'])
async def save_photo(message: types.Message):
    if message.chat.type != 'private' or message.from_user.id != ADMIN_ID:
        return
    photos = load_json(PHOTOS_FILE)
    if message.photo:
        photo_id = message.photo[-1].file_id
        photos.setdefault("all", []).append(photo_id)
        save_json(PHOTOS_FILE, photos)
        await message.answer("✅ Фото сақталды.")
    else:
        await message.answer("⚠️ Фото табылмады.")

@dp.message_handler(content_types=['video'])
async def save_video(message: types.Message):
    if message.chat.type != 'private' or message.from_user.id != ADMIN_ID:
        return
    if '👶' in message.caption:
        videos = load_json(KIDS_VIDEOS_FILE)
    else:
        videos = load_json(VIDEOS_FILE)
    if message.video:
        video_id = message.video.file_id
        videos.setdefault("all", []).append(video_id)
        if '👶' in message.caption:
            save_json(KIDS_VIDEOS_FILE, videos)
        else:
            save_json(VIDEOS_FILE, videos)
        await message.answer("✅ Видео сақталды.")
    else:
        await message.answer("⚠️ Видео табылмады.")

if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    executor.start_polling(dp, skip_updates=True)
