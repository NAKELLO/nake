import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ContentType
from aiogram.utils.deep_linking import get_start_link
from database import *

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
ADMIN_IDS = [7047272652, 6927494520]
CHANNELS = ['@Qazhuboyndar', '@oqigalaruyatsiz']

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

admin_waiting_action = {}
admin_video_type = {}
media_groups = {}

def get_main_keyboard(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton("🛍 Магазин"), KeyboardButton("▶️ Смотреть"), KeyboardButton("🔥 Жанр")
    )
    kb.row(
        KeyboardButton("💎 Заработать"), KeyboardButton("🌸 PREMIUM"), KeyboardButton("💎 Баланс")
    )
    if user_id in ADMIN_IDS:
        kb.add(KeyboardButton("📥 Видео қосу"))
    return kb

def get_video_type_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🧒 Детский", callback_data="watch_kids"))
    kb.add(InlineKeyboardButton("🔞 Взрослый", callback_data="watch_adult"))
    return kb

def get_upload_type_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🧒 Детский", callback_data="upload_kids"))
    kb.add(InlineKeyboardButton("🔞 Взрослый", callback_data="upload_adult"))
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

    await message.answer(
        "Добро пожаловать. 👋\n\nПоздравляю, ты нашёл что искал так долго, нажми на кнопку Смотреть\n\nКнопку Жанр 🔥 это важная кнопка, не забывай его использовать!",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@dp.message_handler(lambda m: m.text == "▶️ Смотреть")
async def watch_handler(message: types.Message):
    await message.answer("Қай видеоны көргіңіз келеді?", reply_markup=get_video_type_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith("watch_"))
async def handle_watch_callback(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    video_type = callback_query.data.replace("watch_", "")
    video = get_random_video(video_type)

    if not video:
        return await callback_query.message.answer("📭 Әзірге видео жоқ. Кейінірек қайта көріңіз.")

    if callback_query.from_user.id not in ADMIN_IDS:
        if get_bonus(user_id) < 3:
            return await callback_query.message.answer("❗ 3 бонус қажет. Достарыңызды шақырыңыз.")
        decrease_bonus(user_id, 3)

    await callback_query.message.answer_video(video)

@dp.message_handler(lambda m: m.text == "💎 Баланс")
async def balance_handler(message: types.Message):
    user_id = str(message.from_user.id)
    bonus = get_bonus(user_id)
    ref_link = await get_start_link(str(user_id), encode=True)
    await message.answer(f"💎 Сізде {bonus} бонус бар.\nДостарыңызды шақырып бонус алыңыз:\n{ref_link}")

@dp.message_handler(lambda m: m.text == "💎 Заработать")
async def earn_handler(message: types.Message):
    await balance_handler(message)

@dp.message_handler(lambda m: m.text == "🌸 PREMIUM")
async def premium_handler(message: types.Message):
    text = (
        "🌸 *PREMIUM қолжетімділік:*\n\n"
        "📆 100 бонус – 1500 ₸\n"
        "📆 200 бонус – 2000 ₸\n"
        "⏳ 1 ай шектеусіз көру – 4000 ₸\n\n"
        "💳 Төлеу үшін админге жазыңыз: @KazHubALU"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "🔥 Жанр")
async def genre_handler(message: types.Message):
    await message.answer("🔖 Жанр таңдаңыз:", reply_markup=get_video_type_keyboard())

@dp.message_handler(lambda m: m.text == "🛍 Магазин")
async def shop_handler(message: types.Message):
    await premium_handler(message)

@dp.message_handler(lambda m: m.text == "📥 Видео қосу")
async def start_video_upload(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Қай бөлімге видео саласыз?", reply_markup=get_upload_type_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith("upload_"))
async def handle_upload_callback(callback_query: types.CallbackQuery):
    video_type = callback_query.data.replace("upload_", "")
    admin_waiting_action[callback_query.from_user.id] = "video_upload"
    admin_video_type[callback_query.from_user.id] = video_type
    await callback_query.message.answer(f"🎬 {video_type.upper()} видеоларды жіберіңіз.")

@dp.message_handler(content_types=ContentType.VIDEO)
async def handle_videos(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    if admin_waiting_action.get(message.from_user.id) != "video_upload":
        return

    video_type = admin_video_type.get(message.from_user.id)
    if not video_type:
        return

    if message.media_group_id:
        media_id = message.media_group_id
        if media_id not in media_groups:
            media_groups[media_id] = []
        media_groups[media_id].append((message, video_type))
        await asyncio.sleep(1.5)
        if media_id in media_groups:
            for msg, vtype in media_groups[media_id]:
                add_video(msg.video.file_id, vtype)
            count = len(media_groups[media_id])
            del media_groups[media_id]
            await message.answer(f"✅ {count} {video_type.upper()} видео сақталды.")
    else:
        add_video(message.video.file_id, video_type)
        await message.answer(f"✅ {video_type.upper()} видео сақталды.")

if __name__ == '__main__':
    from aiogram import executor
    init_db()
    executor.start_polling(dp, skip_updates=True)
