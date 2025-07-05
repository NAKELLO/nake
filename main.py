from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json, os, logging

API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'
ADMIN_ID = 6927494520
BOT_USERNAME = 'Darvinuyatszdaribot'

# Каналдар тізімі
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

    # ⛔ Заң тұлғаларын сүзгіден өткізу
    bad_keywords = ['police', 'gov', 'депутат', 'суд', 'прокуратура', 'din', 'mzrk', 'minjust']
    username = (message.from_user.username or '').lower()
    fullname = (message.from_user.full_name or '').lower()

    for word in bad_keywords:
        if word in username or word in fullname:
            return  # бот үндемейді

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


@dp.message_handler(lambda m: m.text == "🎥 Видео")
async def video_handler(message: types.Message):
    await message.answer("🎬 Видео бөлім әзірленуде.")


@dp.message_handler(lambda m: m.text == "🖼 Фото")
async def photo_handler(message: types.Message):
    await message.answer("📷 Фото бөлім әзірленуде.")


@dp.message_handler(lambda m: m.text == "👶 Детский")
async def kids_handler(message: types.Message):
    await message.answer("👶 Детский бөлім әзірленуде.")


@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    ref = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await message.answer(f"🎁 Сізде {bonus.get(user_id, 0)} бонус бар.\n🔗 Сілтеме: {ref}\n👥 Шақырғандар саны: {len(users[user_id]['invited'])}")


@dp.message_handler(lambda m: m.text == "👥 Қолданушылар саны")
async def user_count(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        users = load_json(USERS_FILE)
        await message.answer(f"👥 Қолданушылар саны: {len(users)}")


@dp.message_handler(lambda m: m.text == "📢 Хабарлама жіберу")
async def broadcast_prompt(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("✉️ Хабарлама мәтінін жазыңыз:")
        admin_waiting_broadcast[message.from_user.id] = True


@dp.message_handler()
async def unknown(message: types.Message):
    if message.chat.type != 'private':
        return
    if admin_waiting_broadcast.get(message.from_user.id):
        admin_waiting_broadcast.pop(message.from_user.id)
        users = load_json(USERS_FILE)
        for user_id in users:
            try:
                await bot.send_message(user_id, message.text)
            except:
                pass
        await message.answer("✅ Хабарлама жіберілді.")
    else:
        await message.answer("Кешіріңіз, тек төмендегі батырмаларды қолданыңыз.")


if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    executor.start_polling(dp, skip_updates=True)
