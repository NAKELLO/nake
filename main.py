from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputMediaVideo, InputFile
import json, os, logging

API_TOKEN = '7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE'
ADMIN_ID = 6927494520
BOT_USERNAME = 'Darvinuyatszdaribot'

# Каналдар тізімі
CHANNELS = ['@Gey_Angime', '@Qazhuboyndar', '@oqigalaruyatsiz']

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

USERS_FILE = 'users.json'
BONUS_FILE = 'bonus.json'
PHOTOS_FILE = 'photos.json'
VIDEOS_FILE = 'videos.json'
KIDS_VIDEOS_FILE = 'kids_videos.json'

admin_waiting_broadcast = {}

def load_json(file):
    try:
        if not os.path.exists(file):
            logging.warning(f"Файл табылмады: {file}")
            return {}
        with open(file, 'r') as f:
            data = json.load(f)
            logging.info(f"Жүктелді: {file} -> {len(data) if isinstance(data, dict) else '??'} жазба")
            return data
    except Exception as e:
        logging.error(f"load_json қатесі: {file} -> {e}")
        return {}

def save_json(file, data):
    try:
        with open(file, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Сақталды: {file} -> {len(data) if isinstance(data, dict) else '??'} жазба")
    except Exception as e:
        logging.error(f"save_json қатесі: {file} -> {e}")

async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# Қалған код өзгеріссіз қалады...
