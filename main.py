from aiogram import Bot, Dispatcher, executor, types
import logging

API_TOKEN = 'ОСЫНДА_ӨЗ_ТОКЕНІҢДІ_ҚОЙ'  # BotFather-дан алынған токен

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Фото қабылдаушы
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    photo_id = message.photo[-1].file_id
    await message.answer(f"✅ Фото сәтті қабылданды!\n🆔 file_id:\n`{photo_id}`", parse_mode="Markdown")

# Видео қабылдаушы
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_video(message: types.Message):
    video_id = message.video.file_id
    await message.answer(f"✅ Видео сәтті қабылданды!\n🆔 file_id:\n`{video_id}`", parse_mode="Markdown")

# Текстке жауап (міндетті емес)
@dp.message_handler()
async def echo_text(message: types.Message):
    await message.answer("📷 Маған фото немесе видео жіберіңіз, мен file_id берем!")

# Ботты іске қосу
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
