import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatMemberStatus

# ====== VARIABLES (Railway Variables арқылы) ======
API_TOKEN = os.getenv("8757577500:AAG7FNMvw54vsg9s343MB-DDCU9kOPS-Esk")        # Жаңа токенді Railway Variables-та қосасың
ADMIN_ID = int(os.getenv("6688100480"))     # 6688100480
CHANNEL_USERNAME = os.getenv("@kazakcombots")  # @kazakcombots

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ====== Қолданушыларды сақтау ======
users_set = set()  # Қолданушылар id сақталады

# ====== Каналга тіркелуді тексеру ======
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

# ====== /start ======
@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    users_set.add(user_id)

    is_subscribed = await check_subscription(user_id)

    if not is_subscribed:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📢 Каналга жазылу",
                url=fhttps://t.me/kazakcombots.replace('@','')}"
            )],
            [InlineKeyboardButton(
                text="✅ Тексеру",
                callback_data="check_sub"
            )]
        ])
        await message.answer(
            "❗ Ботты қолдану үшін каналға тіркелу керек.",
            reply_markup=keyboard
        )
    else:
        await message.answer("✅ Қош келдің! Бот жұмыс істеп тұр 🚀")

# ====== Тексеру кнопкасы ======
@dp.callback_query(F.data == "check_sub")
async def check_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_subscribed = await check_subscription(user_id)

    if is_subscribed:
        await callback.message.edit_text("✅ Рақмет! Енді ботты қолдана аласыз.")
    else:
        await callback.answer("❌ Әлі тіркелмегенсің!", show_alert=True)

# ====== Admin панель ======
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Бұл команда тек админге арналған!")
        return

    total_users = len(users_set)
    text = f"👤 Қолданушылар саны: {total_users}\n\nҚолданушылардың id тізімі:\n{list(users_set)}"
    await message.answer(text)

# ====== RUN ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
