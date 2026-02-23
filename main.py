import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatMemberStatus

# ====== VARIABLES ======
API_TOKEN = "8757577500:AAG7FNMvw54vsg9s343MB-DDCU9kOPS-Esk"
ADMIN_ID = 6688100480
CHANNEL_USERNAME = "@kazakcombots"
# ========================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

users_set = set()
videos = []
photos = []

# ====== Channel subscription check ======
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
    try:
        is_subscribed = await check_subscription(user_id)
    except:
        is_subscribed = True  # егер қате болса, кнопкаларды көрсету

    if not is_subscribed:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Каналга жазылу", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
            [InlineKeyboardButton(text="✅ Тексеру", callback_data="check_sub")]
        ])
        await message.answer("❗ Ботты қолдану үшін каналға тіркелу керек.", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎥 Видео", callback_data="show_video")],
            [InlineKeyboardButton(text="📸 Фото", callback_data="show_photo")]
        ])
        await message.answer("✅ Қош келдің! Бот жұмыс істеп тұр 🚀", reply_markup=keyboard)

# ====== Subscription check callback ======
@dp.callback_query(F.data.in_({"check_sub"}))
async def check_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_subscribed = await check_subscription(user_id)
    if is_subscribed:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎥 Видео", callback_data="show_video")],
            [InlineKeyboardButton(text="📸 Фото", callback_data="show_photo")]
        ])
        await callback.message.edit_text("✅ Рақмет! Енді ботты қолдана аласыз.", reply_markup=keyboard)
    else:
        await callback.answer("❌ Әлі тіркелмегенсің!", show_alert=True)

# ====== Video/Photo callbacks ======
@dp.callback_query(F.data.in_({"show_video","show_photo"}))
async def media_callback(callback: CallbackQuery):
    if callback.data == "show_video":
        if not videos:
            await callback.message.answer("❌ Видео әлі жоқ.")
        else:
            for v in videos:
                await callback.message.answer_video(v)
    elif callback.data == "show_photo":
        if not photos:
            await callback.message.answer("❌ Фото әлі жоқ.")
        else:
            for p in photos:
                await callback.message.answer_photo(p)

# ====== Admin panel ======
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Тек админге арналған!")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Жаңа Видео жүктеу", callback_data="admin_video")],
        [InlineKeyboardButton(text="Жаңа Фото жүктеу", callback_data="admin_photo")],
        [InlineKeyboardButton(text="Қолданушылар санын көру", callback_data="admin_users")]
    ])
    await message.answer("⚙ Админ панель:", reply_markup=keyboard)

@dp.callback_query(F.data.in_({"admin_video","admin_photo","admin_users"}))
async def admin_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Тек админ!", show_alert=True)
        return
    if callback.data == "admin_users":
        await callback.message.answer(f"👤 Қолданушылар саны: {len(users_set)}\n\nID тізімі:\n{list(users_set)}")
    elif callback.data == "admin_video":
        await callback.message.answer("📤 Видео жүктеңіз (admin). URL немесе file_id енгізіңіз:")
    elif callback.data == "admin_photo":
        await callback.message.answer("📤 Фото жүктеңіз (admin). URL немесе file_id енгізіңіз:")

# ====== Run bot ======
async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # ескі getUpdates конфликтін болдырмау
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
