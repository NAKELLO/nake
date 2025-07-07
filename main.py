import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

API_TOKEN = '7748542247:AAGVgKPaOvHH7iDL4Uei2hM_zsI_6gCowkM'
ADMIN_USERNAME = '@KazHubALU'
REQUIRED_CHANNELS = ['@oqigalaruyatsiz', '@Qazhuboyndar']

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://nake-production.up.railway.app")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8000))

# Логгер баптауы
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Бот пен диспетчер
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("🤖 Бот жұмыс істеп тұр!")

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("✅ Webhook орнатылды")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    logger.info("🧹 Webhook тазаланды")

async def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    app.on_startup.append(lambda app: on_startup(bot))
    app.on_shutdown.append(lambda app: on_shutdown(bot))

    print("🚀 Бот іске қосылды")
    return app

if __name__ == '__main__':
    web.run_app(main(), host=WEBAPP_HOST, port=WEBAPP_PORT)
