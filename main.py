from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import json
import os

API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'  # <-- Бот токені
ADMIN_ID = 6927494520  # <-- Админ ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

DATA_FILE = "users.json"

# Файлдан мәліметтерді жүктеу немесе бос база жасау
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = str(message.from_user.id)
    args = message.get_args()

    if user_id not in users:
        users[user_id] = {
            "bonus": 0,
            "invited_by": None
        }

        if args and args != user_id:
            inviter_id = args
            if inviter_id in users:
                users[user_id]["bonus"] += 2
                users[user_id]["invited_by"] = inviter_id
                users[inviter_id]["bonus"] += 1
                await bot.send_message(inviter_id, f"🎉 Жаңа қолданушы сенімен тіркелді! +1 бонус ✨")

    save_data()

    referral_link = f"https://t.me/Darvinuyatszdaribot?start={user_id}"
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🎁 Бонус алу", callback_data="get_bonus"))

    await message.answer(
        f"Қош келдің, {message.from_user.first_name}!\n\n"
        f"Сенің реферальды сілтемең:\n{referral_link}\n\n"
        f"Қазір бонусың: {users[user_id]['bonus']} ⭐️",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data == "get_bonus")
async def get_bonus(call: types.CallbackQuery):
    user_id = str(call.from_user.id)
    bonus = users.get(user_id, {}).get("bonus", 0)
    await call.message.edit_text(f"Сенде {bonus} бонус бар ✨")

@dp.message_handler(commands=['stat'])
async def stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        total = len(users)
        await message.answer(f"📊 Жүйеде барлығы {total} қолданушы тіркелген.")

# ✅ Міне, дұрыс main бөлігі:
if name == 'main':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
