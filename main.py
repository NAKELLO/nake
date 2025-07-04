from aiogram import Bot, Dispatcher, executor, types
import logging
import json
import os

API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'
ADMIN_ID = 6927494520  # Өз Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Контент сақталатын файл
DATA_FILE = "media.json"

# Бар болса, оқимыз
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        media = json.load(f)
else:
    media = {"photos": [], "videos": []}

def save_media():
    with open(DATA_FILE, "w") as f:
        json.dump(media, f)

# 📷 Фото қабылдау (Тек админ)
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def admin_photo_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return  # Басқаларға рұқсат жоқ
    file_id = message.photo[-1].file_id
    media["photos"].append(file_id)
    save_media()
    await message.reply(f"✅ Фото сақталды!\n🆔 file_id:\n`{file_id}`", parse_mode="Markdown")

# 🎥 Видео қабылдау (Тек админ)
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def admin_video_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return  # Басқаларға рұқсат жоқ
    file_id = message.video.file_id
    media["videos"].append(file_id)
    save_media()
    await message.reply(f"✅ Видео сақталды!\n🆔 file_id:\n`{file_id}`", parse_mode="Markdown")

# 📥 Басқа қолданушылар ботты пайдалана алады
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Қош келдіңіз!\n"
        "📷 Фото немесе 🎥 Видео көру үшін бонус жинаңыз!\n"
        "🔄 Ал админ жаңа контент қоса алады."
    )

# 📝 Басқа хабарламаларға жауап
@dp.message_handler()
async def user_message(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("ℹ️ Видео немесе фото көру үшін 'бонус' жинау жүйесін пайдаланыңыз.")
    else:
        await message.answer("📤 Фото немесе видео жіберсеңіз, мен сақтап аламын.")

# 🚀 Ботты іске қосу
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
