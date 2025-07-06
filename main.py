import json
import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.deep_linking import get_start_link, decode_payload

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

def load_json(file):
    if not os.path.exists(file):
        return {} if 'bonus' in file or 'users' in file else {"all": []}
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

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    users = load_json(USERS_FILE)
    bonuses = load_json(BONUS_FILE)

    user_id = str(message.from_user.id)
    payload = message.get_args()

    if user_id not in users:
        users[user_id] = {"ref": payload if payload else None}
        bonuses[user_id] = 2

        if payload and payload != user_id:
            inviter_id = payload
            bonuses[inviter_id] = bonuses.get(inviter_id, 0) + 2

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonuses)

    if not await check_subscription(message.from_user.id):
        channels_list = "\n".join(CHANNELS)
        return await message.answer(f"Ботты пайдалану үшін келесі каналдарға жазылыңыз:\n{channels_list}")

    await message.answer("Қош келдіңіз!", reply_markup=get_main_keyboard(message.from_user.id))

@dp.message_handler(lambda m: m.text == "👶 Детский")
async def kids_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonuses = load_json(BONUS_FILE)
    videos = load_json(KIDS_VIDEOS_FILE)

    if bonuses.get(user_id, 0) < 3:
        return await message.answer("❗ 3 бонус қажет. Бонус жинау үшін достарыңызды шақырыңыз.")

    if not videos["all"]:
        return await message.answer("Әзірге видео жоқ.")

    video = videos["all"][0]
    bonuses[user_id] -= 3

    save_json(BONUS_FILE, bonuses)
    await message.answer_video(video)

@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonuses = load_json(BONUS_FILE)
    bonus = bonuses.get(user_id, 0)
    ref_link = await get_start_link(str(user_id), encode=True)

    await message.answer(f"🎁 Сізде {bonus} бонус бар.\nДостарыңызды шақырып бонус алыңыз:\n{ref_link}")

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

@dp.message_handler(lambda m: m.text == "👥 Қолданушылар саны")
async def user_count(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        users = load_json(USERS_FILE)
        await message.answer(f"Қолданушылар саны: {len(users)}")

@dp.message_handler(lambda m: m.text == "📢 Хабарлама жіберу")
async def broadcast_start(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        admin_waiting_broadcast[message.from_user.id] = True
        await message.answer("Хабарлама мәтінін жіберіңіз:")

@dp.message_handler(content_types=["text", "video"])
async def handle_all(message: types.Message):
    if message.from_user.id in ADMIN_IDS and admin_waiting_broadcast.get(message.from_user.id):
        users = load_json(USERS_FILE)
        for uid in users:
            try:
                if message.video:
                    await bot.send_video(uid, message.video.file_id, caption=message.caption or "")
                else:
                    await bot.send_message(uid, message.text)
            except:
                pass
        admin_waiting_broadcast[message.from_user.id] = False
        return await message.answer("Хабарлама жіберілді!")

    # Видео қосу (тек админ)
    if message.from_user.id in ADMIN_IDS and message.video:
        videos = load_json(KIDS_VIDEOS_FILE)
        videos["all"].append(message.video.file_id)
        save_json(KIDS_VIDEOS_FILE, videos)
        await message.answer("Видео сақталды.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
