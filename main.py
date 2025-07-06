from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json, os, logging

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
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

admin_waiting_broadcast = {}

def load_json(file):
    try:
        if not os.path.exists(file):
            return {"all": []} if 'videos' in file or 'photos' in file else {}
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {"all": []} if 'videos' in file or 'photos' in file else {}

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

@dp.message_handler(lambda m: m.caption and "детский" in m.caption.lower(), content_types=types.ContentType.VIDEO)
async def save_kids_video(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        data = load_json(KIDS_VIDEOS_FILE)
        data['all'].append(message.video.file_id)
        save_json(KIDS_VIDEOS_FILE, data)
        await message.reply("✅ Детский видео сақталды.")

@dp.message_handler(content_types=types.ContentType.VIDEO)
async def save_video(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        data = load_json(VIDEOS_FILE)
        data['all'].append(message.video.file_id)
        save_json(VIDEOS_FILE, data)
        await message.reply("✅ Видео сақталды.")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def save_photo(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        data = load_json(PHOTOS_FILE)
        data['all'].append(message.photo[-1].file_id)
        save_json(PHOTOS_FILE, data)
        await message.reply("✅ Фото сақталды.")

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
        if user_id != str(ADMIN_ID):
            bonus[user_id] = 2

        if message.get_args():
            ref_id = message.get_args()
            if ref_id != user_id and ref_id in users and user_id not in users[ref_id]['invited']:
                users[ref_id]['invited'].append(user_id)
                if ref_id != str(ADMIN_ID):
                    bonus[ref_id] += 2
                    try:
                        await bot.send_message(int(ref_id), "🎉 Сізге 2 бонус қосылды!")
                    except:
                        pass

        save_json(USERS_FILE, users)
        save_json(BONUS_FILE, bonus)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("👶 Детский"), KeyboardButton("🎁 Бонус"))
    kb.add(KeyboardButton("💎 VIP қолжетімділік"))
    if message.from_user.id == ADMIN_ID:
        kb.add(KeyboardButton("📢 Хабарлама жіберу"), KeyboardButton("👥 Қолданушылар саны"))

    await message.answer("Қош келдіңіз!", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    if user_id not in bonus:
        bonus[user_id] = 2
    if user_id not in users:
        users[user_id] = {"videos": 0, "photos": 0, "kids": 0, "invited": []}
    ref = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    save_json(BONUS_FILE, bonus)
    save_json(USERS_FILE, users)
    await message.answer(f"🎁 Сізде {bonus.get(user_id, 0)} бонус бар.\n🔗 Сілтеме: {ref}\n👥 Шақырғандар саны: {len(users[user_id]['invited'])}")

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
        await message.answer("❌ Бұл бөлімді көру үшін 6 бонус қажет. Реферал арқылы жинаңыз.")
        return

    index = users[user_id]["kids"] % len(kids_videos)
    await message.answer_video(kids_videos[index])
    users[user_id]["kids"] += 1
    if message.from_user.id != ADMIN_ID:
        bonus[user_id] -= 6
    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

@dp.message_handler(lambda m: m.text == "💎 VIP қолжетімділік")
async def vip_access(message: types.Message):
    await message.answer(
        """💎 VIP Қолжетімділік:

📦 50 бонус — 2000 тг
📦 100 бонус — 3500 тг
⏳ 1 айлық тегін көру — 6000 тг

📩 Сатып алу үшін: @KazHubALU хабарласыңыз"""
    )

@dp.message_handler(lambda m: m.text == "👥 Қолданушылар саны")
async def user_count(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        users = load_json(USERS_FILE)
        await message.answer(f"👥 Қолданушылар саны: {len(users)}")

@dp.message_handler(lambda m: m.text == "📢 Хабарлама жіберу")
async def ask_broadcast(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        admin_waiting_broadcast[message.from_user.id] = True
        await message.answer("✍️ Хабарлама мәтінін жазыңыз:")

@dp.message_handler()
async def broadcast_or_unknown(message: types.Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID and admin_waiting_broadcast.get(user_id):
        admin_waiting_broadcast.pop(user_id)
        users = load_json(USERS_FILE)
        count = 0
        for uid in users:
            try:
                await bot.send_message(uid, message.text)
                count += 1
            except:
                continue
        await message.answer(f"📨 Хабарлама {count} адамға жіберілді.")
    else:
        await message.answer("🤖 Тек батырмаларды қолданыңыз.")

if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    executor.start_polling(dp, skip_updates=True)
