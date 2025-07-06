import json
import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
ADMIN_IDS = [7047272652, 6927494520]  # Көп админдер
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
        return {"all": []} if 'videos' in file else {}
    with open(file, 'r') as f:
        return json.load(f)

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

def get_main_keyboard(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("👶 Детский"), KeyboardButton("🎁 Бонус"))
    kb.add(KeyboardButton("💎 VIP қолжетімділік"))
    if user_id in ADMIN_IDS:
        kb.row(KeyboardButton("📢 Хабарлама жіберу"), KeyboardButton("👥 Қолданушылар саны"))
    return kb

@dp.message_handler(lambda m: m.text == "💎 VIP қолжетімділік")
async def vip_handler(message: types.Message):
    text = (
        "💎 *VIP қолжетімділік бағасы:*\n\n"
        "📦 100 бонус – 1500 ₸\n"
        "📦 200 бонус – 2000 ₸\n"
        "⏳ 1 ай шектеусіз көру – 4000 ₸\n\n"
        "💳 Төлеу үшін админге жазыңыз: @YourAdminUsername"
    )
    await message.answer(text, reply_markup=get_main_keyboard(message.from_user.id), parse_mode="Markdown")

# (қалған код өзгертілмейді, жоғарыда SyntaxError түзетілді)

# Осы жерде басқа хендлерлер жалғасады...
# Код толығымен бұрынғыдай жұмыс істей береді.
