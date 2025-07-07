import asyncio
import json
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.executor import start_polling

API_TOKEN = '7748542247:AAGVgKPaOvHH7iDL4Uei2hM_zsI_6gCowkM'
ADMIN_IDS = [7047272652, 6927494520]
CHANNELS = ['@Qazhuboyndar', '@oqigalaruyatsiz']

USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'
KIDS_VIDEOS_FILE = 'kids_videos.json'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

media_group_buffer = {}
processing_media_groups = set()

def load_json(file):
    if not os.path.exists(file):
        return {"all": []} if 'videos' in file else {}
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

@dp.message_handler(content_types=types.ContentType.VIDEO, is_media_group=True)
async def save_video_album_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    media_group_id = message.media_group_id
    if media_group_id in processing_media_groups:
        return

    if media_group_id not in media_group_buffer:
        media_group_buffer[media_group_id] = []

    media_group_buffer[media_group_id].append(message)
    processing_media_groups.add(media_group_id)

    await asyncio.sleep(4.0)

    items = media_group_buffer.pop(media_group_id, [])
    processing_media_groups.remove(media_group_id)

    if not items:
        return

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

# --- webhook тазалау ---
async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("🧹 Webhook тазаланды.")

if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    start_polling(dp, skip_updates=True, on_startup=on_startup)
