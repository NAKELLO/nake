import json
import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.executor import start_polling

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
ADMIN_IDS = [7047272652, 6927494520]
CHANNELS = ['@Qazhuboyndar', '@oqigalaruyatsiz']

USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'
KIDS_VIDEOS_FILE = 'kids_videos.json'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

def load_json(file):
    if not os.path.exists(file):
        return {"all": []} if 'videos' in file else {}
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def get_main_keyboard(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("👶 Детский"), KeyboardButton("🎁 Бонус"))
    kb.add(KeyboardButton("💎 VIP қолжетімділік"))
    if user_id in ADMIN_IDS:
        kb.row(KeyboardButton("📢 Хабарлама жіберу"), KeyboardButton("👥 Қолданушылар саны"))
    return kb

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
async def start_handler(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    if user_id not in users:
        if not await check_subscription(message.from_user.id):
            links = "\n".join([f"👉 {c}" for c in CHANNELS])
            await message.answer(f"📛 Ботты қолдану үшін келесі арналарға тіркеліңіз:\n\n{links}\n\n✅ Тіркелген соң /start деп қайта жазыңыз.")
            return

        users[user_id] = {"kids": 0, "invited": []}
        bonus[user_id] = 2

        if message.get_args():
            ref_id = message.get_args()
            if ref_id != user_id and ref_id in users and user_id not in users[ref_id]["invited"]:
                users[ref_id]["invited"].append(user_id)
                bonus[ref_id] = bonus.get(ref_id, 0) + 2
                try:
                    await bot.send_message(int(ref_id), "🎉 Сізге 2 бонус қосылды!")
                except:
                    pass

        save_json(USERS_FILE, users)
        save_json(BONUS_FILE, bonus)

    await message.answer("Қош келдіңіз!", reply_markup=get_main_keyboard(message.from_user.id))

@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    current = bonus.get(user_id, 0)
    await message.answer(f"🎯 Сіздің бонусыңыз: {current}", reply_markup=get_main_keyboard(message.from_user.id))

@dp.message_handler(lambda m: m.text == "💎 VIP қолжетімділік")
async def vip_handler(message: types.Message):
    await message.answer(
        "💎 VIP қолжетімділік:\n\n📦 100 бонус – 1500 ₸\n📦 200 бонус – 2000 ₸\n⏳ 1 ай шектеусіз көру – 4000 ₸\n\nБайланыс: @KazHubALU",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@dp.message_handler(lambda m: m.text == "👶 Детский")
async def kids_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    videos = load_json(KIDS_VIDEOS_FILE).get("all", [])

    if not videos:
        await message.answer("⚠️ Видео қоры бос.", reply_markup=get_main_keyboard(message.from_user.id))
        return

    if user_id not in users:
        users[user_id] = {"kids": 0, "invited": []}

    if message.from_user.id not in ADMIN_IDS and bonus.get(user_id, 0) < 3:
        await message.answer("❌ Бұл бөлімді көру үшін 3 бонус қажет.", reply_markup=get_main_keyboard(message.from_user.id))
        return

    index = users[user_id]["kids"] % len(videos)
    await message.answer_video(videos[index])
    users[user_id]["kids"] += 1

    if message.from_user.id not in ADMIN_IDS:
        bonus[user_id] -= 3

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

# Админ 1 видео жіберсе сақтау
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def save_single_video(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    file_id = message.video.file_id
    data = load_json(KIDS_VIDEOS_FILE)
    if "all" not in data:
        data["all"] = []

    if file_id not in data["all"]:
        data["all"].append(file_id)
        save_json(KIDS_VIDEOS_FILE, data)
        await message.reply("✅ Видео сақталды.")
    else:
        await message.reply("⚠️ Бұл видео бұрыннан бар.")

# Админ альбом (media group) видеоларды жіберсе
@dp.message_handler(content_types=types.ContentType.VIDEO, is_media_group=True)
async def save_video_album_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    media_group_id = message.media_group_id
    if not hasattr(dp, 'media_group_buffer'):
        dp.media_group_buffer = {}

    if media_group_id not in dp.media_group_buffer:
        dp.media_group_buffer[media_group_id] = []

    dp.media_group_buffer[media_group_id].append(message)

    await asyncio.sleep(1.5)

    if dp.media_group_buffer.get(media_group_id):
        items = dp.media_group_buffer.pop(media_group_id)
        kids_videos = load_json(KIDS_VIDEOS_FILE)
        if "all" not in kids_videos:
            kids_videos["all"] = []

        saved_count = 0
        for msg in items:
            file_id = msg.video.file_id
            if file_id not in kids_videos["all"]:
                kids_videos["all"].append(file_id)
                saved_count += 1

        save_json(KIDS_VIDEOS_FILE, kids_videos)
        await message.answer(f"✅ {saved_count} видео сақталды.")

if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    logging.info("✅ Polling басталды...")
    start_polling(dp, skip_updates=True)
