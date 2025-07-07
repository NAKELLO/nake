import asyncio
import json
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web

API_TOKEN = '7748542247:AAGVgKPaOvHH7iDL4Uei2hM_zsI_6gCowkM'
WEBHOOK_HOST = 'https://railway.com/project/0d8983ac-c88d-43c0-bfda-199b06c722f5/service/9c2b7f75-7b1f-4560-a479-1c25559ef21b?environmentId=b56e155d-c171-496f-8c95-14286bb9ec03&id=c4803206-d9a2-4e8b-8848-93f9f3fde86f#deploy'  # 👉 МЫНА ЖЕРГЕ НАҚТЫ Railway сілтемесін жаз
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', 8000))

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

# --- webhook іске қосу ---
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info("📬 Webhook орнатылды")

async def on_shutdown(app):
    logging.warning('⚠️ Бот өшірілуде...')
    await bot.delete_webhook()
    logging.warning('❌ Webhook өшірілді')

app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
app.router.add_post(WEBHOOK_PATH, get_new_configured_app(dispatcher=dp, bot=bot))

if __name__ == '__main__':
    print("🌐 Webhook режимінде бот іске қосылды!")
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
