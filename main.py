from aiogram import Bot, Dispatcher, executor, types
import logging

# 🔐 Мына жерлерге өз мәліметтеріңізді қойыңыз
API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'
ADMIN_ID = 6927494520  # Өз Telegram ID (userinfobot арқылы алыңыз)

# 🔧 Лог
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# 📸 Фото қабылдау (тек админнен)
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Тек админ ғана фото жібере алады.")
    photo_id = message.photo[-1].file_id
    await message.answer(f"✅ Фото сақталды!\n🆔 file_id:\n`{photo_id}`", parse_mode="Markdown")

# 🎥 Видео қабылдау (тек админнен)
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_video(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Тек админ ғана видео жібере алады.")
    video_id = message.video.file_id
    await message.answer(f"✅ Видео сақталды!\n🆔 file_id:\n`{video_id}`", parse_mode="Markdown")

# 📝 Текстке жауап
@dp.message_handler()
async def handle_text(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("👋 Бұл бот тек админге арналған!")
    else:
        await message.answer("📷 Видео немесе фото жіберіңіз, мен сізге file_id қайтарам.")

# 🚀 Ботты іске қосу
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

