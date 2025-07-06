import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.deep_linking import get_start_link
from database import *  # <-- Базаны қосуды ұмытпа!
import os

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'  # <-- Осында өз токеніңді қой!
ADMIN_IDS = [7047272652, 6927494520]
CHANNELS = ['@Qazhuboyndar', '@oqigalaruyatsiz']

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

admin_waiting_broadcast = {}

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
    user_id = str(message.from_user.id)
    payload = message.get_args()

    add_user(user_id, payload if payload else None)

    if payload and payload != user_id:
        add_bonus(payload, 2)

    if not await check_subscription(message.from_user.id):
        channels_list = "\n".join(CHANNELS)
        return await message.answer(f"Ботты пайдалану үшін келесі каналдарға жазылыңыз:\n{channels_list}")

    await message.answer("Қош келдіңіз!", reply_markup=get_main_keyboard(message.from_user.id))

@dp.message_handler(lambda m: m.text == "👶 Детский")
async def kids_handler(message: types.Message):
    user_id = str(message.from_user.id)
    video = get_first_video()
    if not video:
        return await message.answer("Әзірге видео жоқ.")

    if message.from_user.id not in ADMIN_IDS:
        if get_bonus(user_id) < 3:
            return await message.answer("❗ 3 бонус қажет. Достарыңызды шақырыңыз.")
        decrease_bonus(user_id, 3)

    await message.answer_video(video)

@dp.message_handler(lambda m: m.text == "🎁 Бонус")
async def bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = get_bonus(user_id)
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
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "👥 Қолданушылар саны")
async def user_count(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        count = len(get_all_users())
        await message.answer(f"Қолданушылар саны: {count}")

@dp.message_handler(lambda m: m.text == "📢 Хабарлама жіберу")
async def broadcast_start(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        admin_waiting_broadcast[message.from_user.id] = True
        await message.answer("Хабарлама мәтінін жіберіңіз:")

@dp.message_handler(content_types=["video", "text"])
async def handle_all(message: types.Message):
    user_id = message.from_user.id

    if user_id in ADMIN_IDS and admin_waiting_broadcast.get(user_id):
        for uid in get_all_users():
            try:
                if message.video:
                    await bot.send_video(uid, message.video.file_id, caption=message.caption or "")
                else:
                    await bot.send_message(uid, message.text)
            except:
                pass
        admin_waiting_broadcast[user_id] = False
        return await message.answer("Хабарлама жіберілді!")

    if user_id in ADMIN_IDS and message.video:
        add_video(message.video.file_id)
        await message.answer("🎥 Видео сақталды.")

if __name__ == '__main__':
    from aiogram import executor
    init_db()  # ← База дайын болсын
    executor.start_polling(dp, skip_updates=True)
