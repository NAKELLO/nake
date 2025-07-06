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
USERS_FILE = 'users.json'
KIDS_VIDEOS_FILE = 'kids_videos.json'
PHOTOS_FILE = 'photos.json'

# JSON файлдан деректерді жүктеу функциясы
def load_json(file):
    try:
        if not os.path.exists(file):
            return {}
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

# Қолданушыны тіркеу функциясы
def register_user(user_id):
    users_data = load_json(USERS_FILE)
    if str(user_id) not in users_data:
        users_data[str(user_id)] = {"bonus": 0, "referral_link": f"https://t.me/your_bot?start={user_id}"}
        save_json(USERS_FILE, users_data)

# Боттың старт командасын өңдеу
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    register_user(message.from_user.id)
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("👶 Детский"))
    keyboard.add(KeyboardButton("🎁 Бонус"))
    keyboard.add(KeyboardButton("💎 VIP қолжетімділік"))
    if message.from_user.id == ADMIN_ID:
        keyboard.add(KeyboardButton("📢 Хабарлама жіберу"))
        keyboard.add(KeyboardButton("👥 Қолданушылар саны"))
    
    await message.reply("Арналарға тіркелуді сұраймыз.", reply_markup=keyboard)

# Детский видеоларды беру
@dp.message_handler(lambda message: message.text == "👶 Детский")
async def send_kids_video(message: types.Message):
    user_data = load_json(USERS_FILE).get(str(message.from_user.id), {})
    bonus = user_data.get("bonus", 0)

    if message.from_user.id != ADMIN_ID and bonus < 6:
        await message.reply("🚫 Бонустарыңыз жеткіліксіз.")
        return

    # Видео жіберу логикасы (мысалы, тізімнен)
    data = load_json(KIDS_VIDEOS_FILE)
    if data.get('all'):
        video_id = data['all'][0]  # Бірінші видеоны алу (немесе кездейсоқ)
        await bot.send_video(message.chat.id, video_id)

        if message.from_user.id != ADMIN_ID:
            user_data["bonus"] -= 6
            save_json(USERS_FILE, {str(message.from_user.id): user_data})
    else:
        await message.reply("ℹ️ Видео жоқ.")

# Бонустарды көрсету
@dp.message_handler(lambda message: message.text == "🎁 Бонус")
async def show_bonus(message: types.Message):
    user_data = load_json(USERS_FILE).get(str(message.from_user.id), {})
    bonus = user_data.get("bonus", 0)
    referral_link = user_data.get("referral_link", "")
    await message.reply(f"Сіздің бонусыңыз: {bonus}\nШақыру сілтемесі: {referral_link}")

# VIP қолжетімділік
@dp.message_handler(lambda message: message.text == "💎 VIP қолжетімділік")
async def vip_access(message: types.Message):
    await message.reply("💎 VIP қолжетімділік тарифтері:\n1. 100 бонус - VIP қолжетімділік.\n2. 500 бонус - VIP қолжетімділік + арнайы контент.")

# Хабарлама жіберу
@dp.message_handler(lambda message: message.text == "📢 Хабарлама жіберу")
async def broadcast_message(message: types.Message):
    await message.reply("Хабарламаңызды жазыңыз.")
    await dp.current_state(user=message.from_user.id).set_state("broadcast")

@dp.message_handler(state="broadcast")
async def send_broadcast(message: types.Message):
    users_data = load_json(USERS_FILE)
    for user_id in users_data.keys():
        try:
            await bot.send_message(user_id, message.text)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
    await message.reply("📢 Хабарлама барлық қолданушыларға жіберілді.")
    await dp.current_state(user=message.from_user.id).reset_state()

# Қолданушылар санын шығару
@dp.message_handler(lambda message: message.text == "👥 Қолданушылар саны")
async def count_users(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        users_data = load_json(USERS_FILE)
        user_count = len(users_data)
        await message.reply(f"Қолданушылар саны: {user_count}")
    else:
        await message.reply("🚫 Сізде бұл әрекетті орындауға рұқсат жоқ.")

# Фото қабылдау
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def save_photo(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        photos_data = load_json(PHOTOS_FILE)
        photos_data['all'] = photos_data.get('all', [])
        photos_data['all'].append(message.photo[-1].file_id)
        save_json(PHOTOS_FILE, photos_data)
        await message.reply("✅ Фото сақталды.")
    else:
        await message.reply("🚫 Сізде бұл әрекетті орындауға рұқсат жоқ.")

# Видео қабылдау
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def save_video(message: types.Message):
    is_admin = message.from_user.id == ADMIN_ID or (message.forward_from and message.forward_from.id == ADMIN_ID)
    
    if is_admin:
        data = load_json(KIDS_VIDEOS_FILE)
        file_id = message.video.file_id
        if file_id not in data.get('all', []):
            data.setdefault('all', []).append(file_id)
            save_json(KIDS_VIDEOS_FILE, data)
            await message.reply("✅ Видео сақталды.")
        else:
            await message.reply("ℹ️ Бұл видео бұрыннан бар.")
    else:
        await message.reply("🚫 Сізде бұл әрекетті орындауға рұқсат жоқ.")

# Ботты іске қосу
if __name__ == '__main__':
    print("🤖 Бот іске қосылды!")
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
