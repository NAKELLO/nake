from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
import os
import logging

API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'  # <-- Осы жерге өз токеніңді қой
ADMIN_ID = 6927494520  # <-- Өз Telegram ID
CHANNELS = ['@Gey_Angime', '@Qazhuboyndar']

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'

# JSON жүктеу
def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, 'r') as f:
        try:
            return json.load(f)
        except:
            return {}

# JSON сақтау
def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# Арналарға тіркелгенін тексеру
async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

# /start хэндлер
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    # Тек жаңа қолданушылардан тіркелуді талап етеді
    if user_id not in users:
        if not await check_subscription(message.from_user.id):
            text = "🚫 Ботты пайдалану үшін келесі арналарға тіркеліңіз:\n"
            text += "\n".join([f"👉 {c}" for c in CHANNELS])
            text += "\n\n✅ Тіркелген соң /start деп қайта жазыңыз."
            await message.answer(text)
            return

        # Жаңа қолданушы тіркеу
        users[user_id] = {"videos": 0, "photos": 0, "invited": []}
        bonus[user_id] = 2

        if message.get_args():
            ref_id = message.get_args()
            if ref_id != user_id and ref_id in users and user_id not in users[ref_id]["invited"]:
                users[ref_id]["invited"].append(user_id)
                bonus[ref_id] += 2
                try:
                    await bot.send_message(ref_id, "🎉 Сізге 2 бонус қосылды!")
                except:
                    pass

        save_json(USERS_FILE, users)
        save_json(BONUS_FILE, bonus)

    # Меню батырмалары
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎥 Видео"), KeyboardButton("🖼 Фото"))
    kb.add(KeyboardButton("🎁 Бонус"))
    if message.from_user.id == ADMIN_ID:
        kb.add(KeyboardButton("👥 Қолданушылар саны"), KeyboardButton("📢 Хабарлама жіберу"))

    await message.answer("Қош келдіңіз!", reply_markup=kb)

# Ботты іске қосу
if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    executor.start_polling(dp, skip_updates=True)
