import asyncio
import json
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

API_TOKEN = '7748542247:AAGVgKPaOvHH7iDL4Uei2hM_zsI_6gCowkM'

# Railway ішіндегі өз доменіңді WEBHOOK_HOST қып қой
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://nake-production.up.railway.app")
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', 8000))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# Қарапайым хендлер - бот жауап беріп тұрғанын тексереді
@dp.message()
async def echo_all(message: types.Message):
    await message.answer("🤖 Бот жұмыс істеп тұр!")

# Webhook орнату және тазалау
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info("✅ Webhook орнатылды")

async def on_shutdown(app):
    await bot.delete_webhook()
    logging.info("🧹 Webhook өшірілді")

# Webhook қабылдайтын функция
async def handle_webhook(request):
    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.exception("❌ Webhook error")
    return web.Response()

# AIOHTTP серверін орнату
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
app.router.add_post(WEBHOOK_PATH, handle_webhook)

if __name__ == '__main__':
    print("🚀 Webhook іске қосылуда...")
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
