import json
import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
ADMIN_ID = 7047272652
BOT_USERNAME = 'Darvinuyatszdaribot'
CHANNELS = ['@Qazhuboyndar', '@oqigalaruyatsiz']
BLOCKED_CHAT_IDS = [-1002129935121]

USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'
KIDS_VIDEOS_FILE = 'kids_videos.json'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

admin_waiting_broadcast = {}

# 🔧 JSON файлдар
def load_json(file):
    if not os.path.exists(file):
        return {"all": []} if 'videos' in file else {}
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# 🔒 Каналға жазылу тексерісі
async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            logging.warning(f"Subscription check error: {e}")
            return False
    return True

# 🎛️ Батырмаларды жасау
def get_main_keyboard(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("👶 Детский"), KeyboardButton("🎁 Бонус"))
    kb.add(KeyboardButton("💎 VIP қолжетімділік"))
    if str(user_id) == str(ADMIN_ID):
        kb.row(KeyboardButton("📢 Хабарлама жіберу"), KeyboardButton("👥 Қолданушылар саны"))
    return kb

# 🚀 /start командасы
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
        if message.from_user.id != ADMIN_ID:
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

    await message.answer("Қош келдіңіз!", reply_markup=get_main_keyboard(user_id))

# 👶 Детский видео
@dp.message_handler(lambda m: m.text == "👶 Детский")
async def kids_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    kids_videos = load_json(KIDS_VIDEOS_FILE).get("all", [])

    if not kids_videos:
        await message.answer("⚠️ Видео қоры бос.", reply_markup=get_main_keyboard(user_id))
        return

    if user_id not in users:
        users[user_id] = {"kids": 0, "invited": []}

    if message.from_user.id != ADMIN_ID and bonus.get(user_id, 0) < 6:
        await message.answer("❌ Бұл бөлімді көру үшін 6 бонус қажет.", reply_markup=get_main_keyboard(user_id))
        return

    index = users[user_id]["kids"] % len(kids_videos)
    await message.answer_video(kids_videos[index])
    users[user_id]["kids"] += 1
    if message.from_user.id != ADMIN_ID:
        bonus[user_id] -= 6

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

# 🎁 Бонус батырмасы
@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    current = bonus.get(user_id, 0)
    await message.answer(f"🎯 Сіздің бонусыңыз: {current}", reply_markup=get_main_keyboard(user_id))

# 💎 VIP
@dp.message_handler(lambda m: m.text == "💎 VIP қолжетімділік")
async def vip_handler(message: types.Message):
    await message.answer("🔒 VIP бөлімі әзірге қолжетімсіз немесе әкімшіден рұқсат қажет.", reply_markup=get_main_keyboard(message.from_user.id))

# 📢 Хабарлама жіберу сұрау
@dp.message_handler(lambda m: m.text == "📢 Хабарлама жіберу")
async def ask_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    admin_waiting_broadcast[message.from_user.id] = True
    await message.answer("📝 Хабарлама мәтінін жазыңыз:", reply_markup=get_main_keyboard(message.from_user.id))

# 👥 Қолданушылар саны
@dp.message_handler(lambda m: m.text == "👥 Қолданушылар саны")
async def users_count(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_json(USERS_FILE)
    await message.answer(f"📊 Жалпы қолданушылар саны: {len(users)}", reply_markup=get_main_keyboard(message.from_user.id))

# 📤 Хабарламаны жіберу (Broadcast)
@dp.message_handler(lambda m: admin_waiting_broadcast.get(m.from_user.id))
async def broadcast_message(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    admin_waiting_broadcast[message.from_user.id] = False

    users = load_json(USERS_FILE)
    success, fail = 0, 0

    for uid in users:
        try:
            await bot.send_message(uid, f"📢 {message.text}")
            success += 1
        except:
            fail += 1

    await message.answer(f"✅ Жіберілді: {success}, ❌ Қате: {fail}", reply_markup=get_main_keyboard(message.from_user.id))

# 🎥 Видео сақтау
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def save_kids_video(message: types.Message):
    if message.chat.id in BLOCKED_CHAT_IDS:
        return

    is_admin = (
        message.from_user.id == ADMIN_ID or
        (message.forward_from and message.forward_from.id == ADMIN_ID) or
        (message.forward_from_chat and message.forward_from_chat.type == 'channel') or
        (message.sender_chat and message.sender_chat.type == 'channel')
    )

    if is_admin:
        if not message.video:
            await message.reply("⚠️ Видео табылмады.")
            return
        data = load_json(KIDS_VIDEOS_FILE)
        file_id = message.video.file_id
        if file_id not in data['all']:
            data['all'].append(file_id)
            save_json(KIDS_VIDEOS_FILE, data)
            await message.reply("✅ Детский видео сақталды.")
        else:
            await message.reply("ℹ️ Бұл видео бұрыннан бар.")

# ▶️ Ботты іске қосу
if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    logging.info("✅ Polling басталды...")
    executor.start_polling(dp, skip_updates=True)
