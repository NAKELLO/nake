import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

API_TOKEN = "ЖАНА_ТОКЕНДЫ_ОСЫ_ЖЕРГЕ_КОЙ"
ADMIN_ID = 6688100480
CHANNEL_USERNAME = "@kazakcombots"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Каналга тіркелуді тексеру
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
    except:
        return False

# /start командасы
@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    
    is_subscribed = await check_subscription(user_id)

    if not is_subscribed:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Каналга жазылу", url="https://t.me/kazakcombots")],
            [InlineKeyboardButton(text="✅ Тексеру", callback_data="check_sub")]
        ])
        await message.answer(
            "❗ Ботты қолдану үшін каналға тіркелу керек.",
            reply_markup=keyboard
        )
    else:
        await message.answer("✅ Қош келдің! Бот жұмыс істеп тұр.")

# Тексеру кнопкасы
@dp.callback_query(F.data == "check_sub")
async def check_callback(callback):
    user_id = callback.from_user.id
    is_subscribed = await check_subscription(user_id)

    if is_subscribed:
        await callback.message.edit_text("✅ Рақмет! Енді ботты қолдана аласыз.")
    else:
        await callback.answer("❌ Әлі тіркелмегенсің!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
