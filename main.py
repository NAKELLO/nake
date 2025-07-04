from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import json
import os

# 🔐 СЕНІҢ ДЕРЕКТЕРІҢ
API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'  # Бот токен
ADMIN_ID = 6927494520  # Сенің Telegram ID
CHANNELS = ['@darvinteioria', '@Qazhuboyndar']

PHOTO_FILE_ID = 'PHOTO_FILE_ID'  # Фотоның file_id-сі
VIDEO_FILE_ID = 'VIDEO_FILE_ID'  # Видеоның file_id-сі

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

DATA_FILE = "users.json"

# 📂 База жүктеу
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

async def is_subscribed(user_id):
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
    args = message.get_args()

    if user_id not in users:
        users[user_id] = {
            "bonus": 2,
            "invited_by": None,
            "invited": [],
            "viewed": []
        }

        if args and args != user_id:
            inviter_id = args
            if inviter_id in users:
                users[user_id]["invited_by"] = inviter_id
                users[inviter_id]["bonus"] += 2
                users[inviter_id]["invited"].append(user_id)
                await bot.send_message(inviter_id, "🎉 Сіз шақырған адам тіркелді! +2 бонус қосылды ✨")

        save_data()

    if not await is_subscribed(message.from_user.id):
        channels_list = '\n'.join([f'👉 {c}' for c in CHANNELS])
        return await message.answer(f"📢 Жалғастыру үшін мына арналарға тіркеліңіз:\n{channels_list}")

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📷 Фото көру", callback_data="view_photo"),
        InlineKeyboardButton("🎥 Видео көру", callback_data="view_video"),
        InlineKeyboardButton("🎁 Бонус жинау", callback_data="get_bonus")
    )

    await message.answer(
        f"Сәлем, {message.from_user.first_name}!\n\n"
        f"⭐️ Сіздің бонусыңыз: {users[user_id]['bonus']}",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data in ["view_photo", "view_video"])
async def handle_view(call: types.CallbackQuery):
    user_id = str(call.from_user.id)
    action = call.data

    if not await is_subscribed(call.from_user.id):
        channels_list = '\n'.join([f'👉 {c}' for c in CHANNELS])
        return await call.message.answer(f"📢 Жалғастыру үшін мына арналарға тіркеліңіз:\n{channels_list}")

    photo_cost = 4
    video_cost = 3

    if action == "view_photo":
        if users[user_id]['bonus'] >= photo_cost:
            users[user_id]['bonus'] -= photo_cost
            await bot.send_photo(call.from_user.id, PHOTO_FILE_ID, caption="📸 Фотоңыз дайын!")
        else:
            await call.message.answer("❗️ Фото көру үшін 4 бонус қажет.\n🎁 Реферал арқылы бонус жинаңыз.")
    elif action == "view_video":
        if users[user_id]['bonus'] >= video_cost:
            users[user_id]['bonus'] -= video_cost
            await bot.send_video(call.from_user.id, VIDEO_FILE_ID, caption="🎬 Видео дайын!")
        else:
            await call.message.answer("❗️ Видео көру үшін 3 бонус қажет.\n🎁 Реферал арқылы бонус жинаңыз.")

    save_data()

@dp.callback_query_handler(lambda c: c.data == "get_bonus")
async def get_bonus(call: types.CallbackQuery):
    user_id = str(call.from_user.id)
    bot_info = await bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={user_id}"

    await call.message.answer(
        f"🔗 Реферал сілтемеңіз:\n{referral_link}\n\n"
        f"Әр тіркелген адам үшін +2 бонус аласыз!"
    )

@dp.message_handler(commands=['stat'])
async def stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        total = len(users)
        await message.answer(f"📊 Жалпы тіркелген қолданушылар саны: {total}")

# ⭐️ Дұрыс басталу блогы
if name == 'main':
    executor.start_polling(dp, skip_updates=True)
