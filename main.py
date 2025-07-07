import json
import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
ADMIN_IDS = [7047272652, 1234567890]  # Бірнеше админ ID осында жазылады
CHANNELS = ['@Qazhuboyndar', '@oqigalaruyatsiz']
BLOCKED_CHAT_IDS = [-1002129935121]

USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'
KIDS_VIDEOS_FILE = 'kids_videos.json'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

admin_waiting_broadcast = {}

# JSON жүктеу/сақтау
def load_json(file):
    if not os.path.exists(file):
        return {"all": []} if 'videos' in file else {}
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# Каналға жазылуды тексеру
async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# Бас меню
def get_main_keyboard(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("👶 Детский"), KeyboardButton("🎁 Бонус"))
    kb.add(KeyboardButton("💎 VIP қолжетімділік"))
    if user_id in ADMIN_IDS:
        kb.row(KeyboardButton("📢 Хабарлама жіберу"), KeyboardButton("👥 Қолданушылар саны"))
    return kb

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

# 👶 Детский видео
@dp.message_handler(lambda m: m.text == "👶 Детский")
async def kids_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    kids_videos = load_json(KIDS_VIDEOS_FILE).get("all", [])

    if not kids_videos:
        await message.answer("⚠️ Видео қоры бос.", reply_markup=get_main_keyboard(message.from_user.id))
        return

    if user_id not in users:
        users[user_id] = {"kids": 0, "invited": []}

    user_bonus = bonus.get(user_id, 0)
    if message.from_user.id not in ADMIN_IDS and user_bonus < 3:
        await message.answer("❌ Бұл бөлімді көру үшін 3 бонус қажет.", reply_markup=get_main_keyboard(message.from_user.id))
        return

    index = users[user_id]["kids"] % len(kids_videos)
    await message.answer_video(kids_videos[index])
    users[user_id]["kids"] += 1

    if message.from_user.id not in ADMIN_IDS:
        bonus[user_id] -= 3

        for ref_id, data in users.items():
            if user_id in data.get("invited", []):
                if ref_id not in [str(aid) for aid in ADMIN_IDS]:
                    bonus[ref_id] = bonus.get(ref_id, 0) + 1
                    try:
                        await bot.send_message(int(ref_id), "👶 Сіздің реферал видео көрді — сізге 1 бонус қосылды!")
                    except:
                        pass
                break

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

# 🎁 Бонус
@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    current = bonus.get(user_id, 0)
    await message.answer(f"🎯 Сіздің бонусыңыз: {current}", reply_markup=get_main_keyboard(message.from_user.id))

# 💎 VIP
@dp.message_handler(lambda m: m.text == "💎 VIP қолжетімділік")
async def vip_handler(message: types.Message):
    text = (
        "💎 *VIP қолжетімділік бағасы:*\n\n"
        "📦 100 бонус – 1500 ₸\n"
        "📦 200 бонус – 2000 ₸\n"
       
