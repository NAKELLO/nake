import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatMemberStatus

# ====== VARIABLES ======
API_TOKEN = os.getenv("8757577500:AAG7FNMvw54vsg9s343MB-DDCU9kOPS-Esk")
ADMIN_ID = int(os.getenv("6303091468"))
CHANNEL_USERNAME = os.getenv("@kazakcombots")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ====== Қолданушылар мен контент сақтау (memory-де) ======
users_set = set()
videos = []  # видеолар
photos = []  # фотолар

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
                url=f"https://t.me/kazakcombots.replace('@','')}"
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
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎥 Видео", callback_data="show_video")],
            [InlineKeyboardButton(text="📸 Фото", callback_data="show_photo")]
        ])
        await message.answer("✅ Қош келдің! Таңдаңыз:", reply_markup=keyboard)

# ====== Тексеру кнопкасы ======
@dp.callback_query(F.data == "check_sub")
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

# ====== Видео/Фото көрсету ======
@dp.callback_query(F.data == "show_video")
async def show_video(callback: CallbackQuery):
    if not videos:
        await callback.message.answer("❌ Видео әлі жоқ.")
    else:
        for v in videos:
            await callback.message.answer_video(v)

@dp.callback_query(F.data == "show_photo")
async def show_photo(callback: CallbackQuery):
    if not photos:
        await callback.message.answer("❌ Фото әлі жоқ.")
    else:
        for p in photos:
            await callback.message.answer_photo(p)

# ====== Admin панель ======
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Бұл команда тек админге арналған!")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Жаңа Видео жүктеу", callback_data="admin_video")],
        [InlineKeyboardButton(text="Жаңа Фото жүктеу", callback_data="admin_photo")],
        [InlineKeyboardButton(text="Қолданушылар санын көру", callback_data="admin_users")]
    ])
    await message.answer("⚙ Админ панель:", reply_markup=keyboard)

# ====== Admin кнопкалары ======
@dp.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    total_users = len(users_set)
    text = f"👤 Қолданушылар саны: {total_users}\n\nID тізімі:\n{list(users_set)}"
    await callback.message.answer(text)

@dp.callback_query(F.data == "admin_video")
async def admin_add_video(callback: CallbackQuery):
    await callback.message.answer("📤 Видео жүктеңіз (admin тек):")
    # келесі хабарламаны await dp.message.listen арқылы алу керек
    # Қазіргі нұсқада memory-де сақтау

@dp.callback_query(F.data == "admin_photo")
async def admin_add_photo(callback: CallbackQuery):
    await callback.message.answer("📤 Фото жүктеңіз (admin тек):")
    # келесі хабарламаны await dp.message.listen арқылы алу керек
    # Қазіргі нұсқада memory-де сақтау

# ====== RUN ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
