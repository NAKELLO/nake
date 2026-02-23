import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus

# ====== VARIABLES ======
API_TOKEN = "8757577500:AAG7FNMvw54vsg9s343MB-DDCU9kOPS-Esk"
ADMIN_ID = 6688100480
CHANNEL_USERNAME = "@kazakcombots"
# ========================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

users_set = set()  # қолданушыларды сақтау

async def check_subscription(user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
    except:
        return False

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    users_set.add(user_id)

    is_subscribed = await check_subscription(user_id)

    if not is_subscribed:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Каналга жазылу", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
            [InlineKeyboardButton(text="✅ Тексеру", callback_data="check_sub")]
        ])
        await message.answer(
            "❗ Ботты қолдану үшін каналға тіркелу керек.",
            reply_markup=keyboard
        )
    else:
        await message.answer("✅ Қош келдің! Бот жұмыс істеп тұр 🚀")

@dp.callback_query(F.data.in_({"check_sub"}))
async def check_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_subscribed = await check_subscription(user_id)

    if is_subscribed:
        await callback.message.edit_text("✅ Рақмет! Енді ботты қолдана аласыз.")
    else:
        await callback.answer("❌ Әлі тіркелмегенсің!", show_alert=True)

async def main():
    # Ескі getUpdates конфликтін болдырмау
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
