import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Токен мен администратор идентификаторын енгізіңіз
API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'  # Сіздің токеніңіз
ADMIN_ID = 6927494520  # Сіздің Telegram идентификаторыңыз

# Лог жазу конфигурациясы
logging.basicConfig(level=logging.INFO)

# Бот пен диспетчерді инициализациялау
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Файлдар
KIDS_VIDEOS_FILE = 'kids_videos.json'

# JSON файлдан деректерді жүктеу функциясы
def load_json(file):
    try:
        if not os.path.exists(file):
            return {"all": []}
        with open(file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error(f"Ошибка декодирования JSON в файле {file}.")
        return {}
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла {file}: {e}")
        return {}

# JSON файлға деректерді сақтау функциясы
def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# Видео сақтайтын хэндлер
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def save_kids_video(message: types.Message):
    # Администратор тексерісі
    is_admin = (
        message.from_user.id == ADMIN_ID or
        (message.forward_from and message.forward_from.id == ADMIN_ID) or
        (message.forward_from_chat and message.forward_from_chat.type == 'channel') or
        (message.sender_chat and message.sender_chat.type == 'channel')
    )

    if is_admin:
        data = load_json(KIDS_VIDEOS_FILE)
        file_id = message.video.file_id
        if file_id not in data['all']:
            data['all'].append(file_id)
            save_json(KIDS_VIDEOS_FILE, data)
            await message.reply("✅ Детский видео сақталды.")
        else:
            await message.reply("ℹ️ Бұл видео бұрыннан бар.")
    else:
        await message.reply("🚫 Сізде бұл әрекетті орындауға рұқсат жоқ.")

# Боттың старт командасын өңдеу
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🤖 Бот іске қосылды! Сізге қалай көмектесе аламын?")

# Ботты іске қосу
if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
