import json
import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
ADMIN_IDS = [7047272652, 6927494520]
CHANNELS = ['@Qazhuboyndar', '@oqigalaruyatsiz']
BLOCKED_CHAT_IDS = [-1002129935121]

USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'
KIDS_VIDEOS_FILE = 'kids_videos.json'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

admin_waiting_broadcast = {}

# JSON жүктеу / сақтау
def load_json(file):
    if not os.path.exists(file):
        return {"all": []} if 'videos' in file else {}
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# Арнаға жазылғанын тексеру
async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# Батырмалар
def get_main_keyboard(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("👶 Детский"), KeyboardButton("🎁 Бонус"))
    kb.add(KeyboardButton("💎 VIP қолжетімділік"))
    if user_id in ADMIN_IDS:
        kb.row(KeyboardButton("📢 Хабарлама жіберу"), KeyboardButton("👥 Қолданушылар саны"))
    return kb

# VIP info
@dp.message_handler(lambda m: m.text == "💎 VIP қолжетімділік")
async def vip_handler(message: types.Message):
    text = (
        "💎 *VIP қолжетімділік бағасы:*\n\n"
        "📦 100 бонус – 1500 ₸\n"
        "📦 200 бонус – 2000 ₸\n"
        "⏳ 1 ай шектеусіз көру – 4000 ₸\n\n"
        "💳 Төлеу үшін админге жазыңыз: @KazHubALU"
    )
    await message.answer(text, reply_markup=get_main_keyboard(message.from_user.id), parse_mode="Markdown")

# /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type != 'private':
        return

    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    if user_id not in users:
        if not await check_subscription(message.from_user.id):
            links = "\n".join([f"👉 {c}" for c in CHANNELS])
            await message.answer(f"📛 Ботты қолдану үшін келесі арналарға тіркеліңіз:\n\n{links}\n\n✅ Тіркелген соң /start деп қайта жазыңыз.")
            return

        users[user_id] = {"kids": 0, "invited": []}
        if message.from_user.id not in ADMIN_IDS:
            bonus[user_id] = 2

        if message.get_args():
            ref_id = message.get_args()
            if ref_id != user_id and ref_id in users and user_id not in users[ref_id]['invited']:
                users[ref_id]['invited'].append(user_id)
                if ref_id not in [str(aid) for aid in ADMIN_IDS]:
                    bonus[ref_id] = bonus.get(ref_id, 0) + 2
                    try:
                        await bot.send_message(int(ref_id), "🎉 Сізге 2 бонус қосылды!")
                    except:
                        pass

        save_json(USERS_FILE, users)
        save_json(BONUS_FILE, bonus)

    await message.answer("Қош келдіңіз!", reply_markup=get_main_keyboard(message.from_user.id))

# 🎁 Бонус
@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    bonus = load_json(BONUS_FILE)
    user_id = str(message.from_user.id)
    count = bonus.get(user_id, 0)
    await message.answer(f"🎁 Сіздің бонусыңыз: {count}")

# 👶 Детский
@dp.message_handler(lambda m: m.text == "👶 Детский")
async def send_kids_videos(message: types.Message):
    kids_data = load_json(KIDS_VIDEOS_FILE)
    videos = kids_data.get("all", [])
    if not videos:
        await message.answer("👶 Бұл бөлімде видеолар жоқ.")
        return
    for video_id in videos:
        try:
            await bot.send_video(message.chat.id, video_id)
        except:
            await message.answer("⚠️ Видео жүктеу қатесі орын алды.")

# Админ видео жүктеу
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_video(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    file_id = message.video.file_id
    kids_data = load_json(KIDS_VIDEOS_FILE)
    if 'all' not in kids_data:
        kids_data['all'] = []
    kids_data['all'].append(file_id)
    save_json(KIDS_VIDEOS_FILE, kids_data)
    await message.answer("✅ Видео сақталды (Детский категориясына)")

# 👥 Қолданушылар саны
@dp.message_handler(lambda m: m.text == "👥 Қолданушылар саны" and m.from_user.id in ADMIN_IDS)
async def user_count_handler(message: types.Message):
    users = load_json(USERS_FILE)
    await message.answer(f"📊 Жалпы қолданушылар саны: {len(users)}")

# 📢 Хабарлама жіберу
@dp.message_handler(lambda m: m.text == "📢 Хабарлама жіберу" and m.from_user.id in ADMIN_IDS)
async def broadcast_start(message: types.Message):
    admin_waiting_broadcast[message.from_user.id] = True
    await message.answer("✉️ Хабарламаңызды жазыңыз, барлық қолданушыларға жіберіледі.")

@dp.message_handler(lambda m: m.from_user.id in ADMIN_IDS)
async def handle_admin_broadcast(message: types.Message):
    if admin_waiting_broadcast.get(message.from_user.id):
        users = load_json(USERS_FILE)
        sent = 0
        for user_id in users:
            try:
                await bot.send_message(int(user_id), message.text)
                sent += 1
            except:
                pass
        admin_waiting_broadcast[message.from_user.id] = False
        await message.answer(f"✅ Хабарлама {sent} адамға жіберілді.")

# Бастау
if name == 'main':
    print("🤖 Бот іске қосылды!")
    logging.info("✅ Polling басталды...")
    executor.start_polling(dp, skip_updates=True)
