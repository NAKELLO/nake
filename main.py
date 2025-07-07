import logging, json, os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = 'ТВОЙ_БОТ_ТОКЕН'
ADMIN_ID = 6927494520  # Өз ID-ң

bot = Bot(7748542247:AAEPCvB-3EFngPPv45SvBG_Nizh0qQmpwB4)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

VIDEOS_FILE = "videos.json"
videos = []
state = {}

# 📂 Файлдан жүктеу
if os.path.exists(VIDEOS_FILE):
    with open(VIDEOS_FILE, "r") as f:
        videos = json.load(f)

# 💾 Файлға сақтау
def save_videos():
    with open(VIDEOS_FILE, "w") as f:
        json.dump(videos, f, indent=2)

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

# 📝 Атауы
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
    cat = "kids" if "Детский" in msg.text else "adult"
    found = [v for v in videos if v["category"] == cat]
    if not found:
        await msg.reply("📂 Видео жоқ.")
        return
    for v in found:
        await bot.send_video(msg.chat.id, v["file_id"], caption=f"{v['title']} — {v['cost']} бонус")

# 📍 Start (міндетті емес)
@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("👶 Детский", "🔞 Взрослый")
    await msg.reply("Категория таңда:", reply_markup=kb)

if name == "main":
    executor.start_polling(dp, skip_updates=True)
