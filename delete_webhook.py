from aiogram import Bot
import asyncio

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'  # ← мұнда өзіңіздің нақты токеніңізді жазыңыз

async def delete_webhook():
    bot = Bot(token=API_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook өшірілді.")

asyncio.run(delete_webhook())
