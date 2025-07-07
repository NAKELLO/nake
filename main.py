import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔐 Token мен Admin ID
API_TOKEN = '7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4'
ADMIN_ID = 6927494520
CHANNELS = ['@oqigalaruyatsiz', '@Qazhuboyndar']

# 🔧 Bot және Dispatcher
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# 📂 Файлдар
VIDEOS_FILE = "videos.json"
USERS_FILE = "users.json"
videos = []
users = {}
state = {}

# 📥 Видео мен қолданушыларды жүктеу
if os.path.exists(VIDEOS_FILE):
    with open(VIDEOS_FILE, "r", encoding="utf-8") as f:
        videos = json.load(f)

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

# 💾 Сақтау функциялары
def save_videos():
    with open(VIDEOS_FILE, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2)

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

# 🔄 Каналға тіркелгенін тексеру
async def check_subscriptions(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# 👨‍💻 Админ видео жібереді
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def video_upload(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    state[msg.from_user.id] = {
        "file_id": msg.video.file_id,
        "step": "title"
    }
    await msg.reply("🎬 Видео атауын жазыңыз:")

# 📝 Видео атауын енгізу
@dp.message_handler(lambda m: state.get(m.from_user.id, {}).get("step") == "title")
async def video_title(msg: types.Message):
    state[msg.from_user.id]["title"] = msg.text
    state[msg.from_user.id]["step"] = "category"
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("👶 Детский", callback_data="cat_kids"),
        InlineKeyboardButton("🔞 Взрослый", callback_data="cat_adult")
    )
    await msg.reply("📁 Категория таңдаңыз:", reply_markup=kb)

# 📁 Категория таңдау
@dp.callback_query_handler(lambda c: c.data.startswith("cat_"))
async def category_set(c: types.CallbackQuery):
    cat = "kids" if c.data == "cat_kids" else "adult"
    state[c.from_user.id]["category"] = cat
    state[c.from_user.id]["step"] = "cost"
    await c.message.edit_text("💰 Қанша бонус қажет?")

# 💰 Бонус енгізу
@dp.message_handler(lambda m: state.get(m.from_user.id, {}).get("step") == "cost")
async def set_cost(msg: types.Message):
    try:
        cost = int(msg.text)
        st = state.pop(msg.from_user.id)
        video = {
            "id": len(videos) + 1,
            "title": st["title"],
            "file_id": st["file_id"],
            "category": st["category"],
            "cost": cost
        }
        videos.append(video)
        save_videos()
        await msg.reply("✅ Видео сақталды!")
    except:
        await msg.reply("❗ Бонус санын дұрыс жазыңыз!")

# 🎬 Видео көру
@dp.message_handler(lambda m: m.text == "👶 Детский" or m.text == "🔞 Взрослый")
async def show_category(msg: types.Message):
    user_id = str(msg.from_user.id)

    if not await check_subscriptions(user_id):
        kb = InlineKeyboardMarkup(row_width=1)
        for ch in CHANNELS:
            kb.add(InlineKeyboardButton(f"Тіркелу: {ch}", url=f"https://t.me/{ch[1:]}", callback_data="sub"))
        kb.add(InlineKeyboardButton("✅ Тіркелдім", callback_data="check_sub"))
        await msg.reply("Ботты қолдану үшін каналдарға тіркеліңіз:", reply_markup=kb)
        return

    if user_id not in users or users[user_id]["balance"] < 1:
        await msg.reply("❗ Сіздің бонусыңыз жеткіліксіз. Досыңызды шақырып бонус алыңыз!")
        return

    cat = "kids" if "Детский" in msg.text else "adult"
    found = [v for v in videos if v["category"] == cat]
    if not found:
        await msg.reply("📂 Бұл категорияда видео жоқ.")
        return

    for v in found:
        if users[user_id]["balance"] >= v["cost"]:
            await bot.send_video(
                msg.chat.id,
                v["file_id"],
                caption=f"{v['title']} — {v['cost']} бонус"
            )
            users[user_id]["balance"] -= v["cost"]
            save_users()
        else:
            await msg.reply(f"❗ Бұл видеоны көру үшін {v['cost']} бонус қажет. Сіздің бонус: {users[user_id]['balance']}")

# 📍 /start командасы
@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    user_id = str(msg.from_user.id)
    ref = msg.get_args()
    if user_id not in users:
        users[user_id] = {"balance": 2, "ref": ref if ref and ref != user_id else None}
        if ref and ref in users:
            users[ref]["balance"] += 2
    save_users()

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("👶 Детский", "🔞 Взрослый")
    await msg.reply("Категория таңдаңыз:", reply_markup=kb)

# 📊 Статистика және 📢 рассылка
@dp.message_handler(lambda m: m.text == "📊 Статистика" and m.from_user.id == ADMIN_ID)
async def stats(msg: types.Message):
    total = len(users)
    await msg.reply(f"👥 Барлық қолданушы: {total}")

@dp.message_handler(lambda m: m.text == "📢 Рассылка" and m.from_user.id == ADMIN_ID)
async def ask_broadcast(msg: types.Message):
    state[msg.from_user.id] = {"step": "broadcast"}
    await msg.reply("📨 Хабарламаңызды жазыңыз:")

@dp.message_handler(lambda m: state.get(m.from_user.id, {}).get("step") == "broadcast")
async def send_broadcast(msg: types.Message):
    text = msg.text
    state.pop(msg.from_user.id)
    count = 0
    for uid in users:
        try:
            await bot.send_message(uid, text)
            count += 1
        except:
            continue
    await msg.reply(f"✅ Жіберілді: {count} қолданушыға")

# 🔁 Ботты іске қосу
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
