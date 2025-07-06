from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json, os, logging

API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
ADMIN_ID = 6927494520
BOT_USERNAME = 'Darvinuyatszdaribot'

BLOCKED_CHAT_IDS = [-1002129935121]  # @Gey_Angime ID
CHANNELS = ['@Qazhuboyndar', '@oqigalaruyatsiz']

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
            return {"all": []} if 'videos' in file or 'photos' in file else {}
        with open(file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {file}: {e}")
        return {"all": []} if 'videos' in file or 'photos' in file else {}

def save_json(file, data):
    try:
        with open(file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[INFO] Saved file: {file}, items: {len(data.get('all', []))}")
    except Exception as e:
        print(f"[ERROR] Failed to save {file}: {e}")

async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

@dp.message_handler(content_types=types.ContentType.VIDEO)
async def save_kids_video(message: types.Message):
    if message.chat.id in BLOCKED_CHAT_IDS:
        return

    is_admin = message.from_user.id == ADMIN_ID or (
        message.forward_from and message.forward_from.id == ADMIN_ID
    )

    if is_admin:
        try:
            data = load_json(KIDS_VIDEOS_FILE)
            file_id = message.video.file_id
            print(f"[DEBUG] Received video with file_id: {file_id}")

            if file_id not in data['all']:
                data['all'].append(file_id)
                save_json(KIDS_VIDEOS_FILE, data)
                await message.reply("✅ Детский видео сақталды.")
            else:
                await message.reply("ℹ️ Бұл видео бұрыннан сақталған.")
        except Exception as e:
            await message.reply("❌ Видео сақтау кезінде қате шықты.")
            print(f"[ERROR] Failed to save kids video: {e}")
    else:
        print(f"[INFO] User {message.from_user.id} is not admin. Video ignored.")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def save_photo(message: types.Message):
    if message.chat.id in BLOCKED_CHAT_IDS:
        return
    if message.from_user.id == ADMIN_ID:
        data = load_json(PHOTOS_FILE)
        if message.photo[-1].file_id not in data['all']:
            data['all'].append(message.photo[-1].file_id)
            save_json(PHOTOS_FILE, data)
            await message.reply("✅ Фото сақталды.")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type != 'private':
        return

    user_id = str(message.from_user.id)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    if user_id not in users:
        is_subscribed = await check_subscription(message.from_user.id)
        if not is_subscribed:
            links = "\n".join([f"👉 {c}" for c in CHANNELS])
            await message.answer(f"📛 Ботты қолдану үшін келесі арналарға тіркеліңіз:\n\n{links}\n\n✅ Тіркелген соң /start деп қайта жазыңыз.")
            return

        users[user_id] = {"videos": 0, "photos": 0, "kids": 0, "invited": []}
        if user_id != str(ADMIN_ID):
            bonus[user_id] = 2

        if message.get_args():
            ref_id = message.get_args()
            if ref_id != user_id and ref_id in users and user_id not in users[ref_id]['invited']:
                users[ref_id]['invited'].append(user_id)
                if ref_id != str(ADMIN_ID):
                    bonus[ref_id] += 2
                    try:
                        await bot.send_message(int(ref_id), "🎉 Сізге 2 бонус қосылды!")
                    except:
                        pass

        save_json(USERS_FILE, users)
        save_json(BONUS_FILE, bonus)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("👶 Детский"), KeyboardButton("🎁 Бонус"))
    kb.add(KeyboardButton("💎 VIP қолжетімділік"))
    if message.from_user.id == ADMIN_ID:
        kb.add(KeyboardButton("📢 Хабарлама жіберу"), KeyboardButton("👥 Қолданушылар саны"))

    await message.answer("Қош келдіңіз!", reply_markup=kb)

# Қалған хендлерлер өзгеріссіз қалдырылды
