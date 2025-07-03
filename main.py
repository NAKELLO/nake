import telebot
from telebot import types
import json
import os

# Бот токен мен админ ID
TOKEN = '7748542247:AAH_y9C_LPTHDp74WNHN4HZHLpl-NuB-13s'
ADMIN_ID = 6927494520

# Каналдар
CHANNELS = ['@Gey_Angime', '@Qazhuboyndar']

bot = telebot.TeleBot(TOKEN)

# Файл жолдары
USERS_FILE = 'users.json'
PHOTOS_FILE = 'photos.json'
VIDEOS_FILE = 'videos.json'
BONUS_FILE = 'bonus.json'

# JSON функциялары
def load_json(file):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)
    with open(file, 'r') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# Арнаға тіркелу тексерісі
def is_subscribed(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

# /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)

    if not is_subscribed(message.from_user.id):
        join_links = "\n".join([f"👉 {link}" for link in CHANNELS])
        bot.send_message(
            message.chat.id,
            f"🚫 Ботты қолдану үшін төмендегі каналдарға тіркеліңіз:\n\n{join_links}\n\nТіркелген соң /start деп қайта жазыңыз."
        )
        return

    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    if user_id not in users:
        users[user_id] = {
            'videos': 0,
            'photos': 0,
            'invited': [],
        }
        bonus[user_id] = 0

        if message.text.startswith('/start ') and len(message.text.split()) == 2:
            ref_id = message.text.split()[1]
            if ref_id != user_id and ref_id in users:
                if user_id not in users[ref_id]['invited']:
                    users[ref_id]['invited'].append(user_id)
                    bonus[ref_id] += 2
                    bot.send_message(ref_id, '🎉 Сізге 2 бонус жазылды!')

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🎥 Видео', '🖼 Фото', '🎁 Бонус', '🛒 Сатып алу')
    if message.from_user.id == ADMIN_ID:
        markup.add('📢 Хабарлама жіберу')

    bot.send_message(message.chat.id, 'Қош келдіңіз!', reply_markup=markup)

# Видео көру
@bot.message_handler(func=lambda m: m.text == '🎥 Видео')
def send_video(message):
    user_id = str(message.from_user.id)
    videos = load_json(VIDEOS_FILE)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    video_list = videos.get('all', [])
    index = users[user_id]['videos'] % len(video_list) if video_list else 0

    if bonus.get(user_id, 0) > 0 and video_list:
        bot.send_video(message.chat.id, video_list[index])
        users[user_id]['videos'] += 1
        bonus[user_id] -= 1
    elif not video_list:
        bot.send_message(message.chat.id, 'Әзірге видео жоқ.')
    else:
        bot.send_message(message.chat.id, 'Бонус жетіспейді, шақыру арқылы жинаңыз.')

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

# Фото көру
@bot.message_handler(func=lambda m: m.text == '🖼 Фото')
def send_photo(message):
    user_id = str(message.from_user.id)
    photos = load_json(PHOTOS_FILE)
    users = load_json(USERS_FILE)
    bonus = load_json(BONUS_FILE)

    photo_list = photos.get('all', [])
    index = users[user_id]['photos'] % len(photo_list) if photo_list else 0

    if bonus.get(user_id, 0) > 0 and photo_list:
        bot.send_photo(message.chat.id, photo_list[index])
        users[user_id]['photos'] += 1
        bonus[user_id] -= 1
    elif not photo_list:
        bot.send_message(message.chat.id, 'Әзірге фото жоқ.')
    else:
        bot.send_message(message.chat.id, 'Бонус жетіспейді, шақыру арқылы жинаңыз.')

    save_json(USERS_FILE, users)
    save_json(BONUS_FILE, bonus)

# Бонус
@bot.message_handler(func=lambda m: m.text == '🎁 Бонус')
def check_bonus(message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    ref_link = f'https://t.me/Darvinuyatszdaribot?start={user_id}'
    invited = users.get(user_id, {}).get('invited', [])
    bot.send_message(
        message.chat.id,
        f'Сізде {bonus.get(user_id, 0)} бонус бар.\n'
        f'Сіз {len(invited)} адам шақырдыңыз.\n'
        f'Шақыру сілтемеңіз: {ref_link}'
    )

# Сатып алу
@bot.message_handler(func=lambda m: m.text == '🛒 Сатып алу')
def buy(message):
    text = (
        '450 видеосы бар аралас 500 тг\n'
        'Детский аралас 1000 тг\n'
        'Чисто детский 1500 тг +2 канал қосып береміз\n'
        '2000 тг 5 канал\n'
        '2500 тг 10 канал\n'
        '3000 тг 20 канал жоғарыдағылардың бәрін алу\n'
        'Жаз: @KazHubALU'
    )
    bot.send_message(message.chat.id, text)

# Хабарлама тарату (тек админге)
@bot.message_handler(func=lambda m: m.text == '📢 Хабарлама жіберу')
def admin_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, 'Жібергіңіз келетін хабарламаны жазыңыз:')
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(msg):
    users = load_json(USERS_FILE)
    for user_id in users:
        try:
            bot.send_message(user_id, msg.text)
        except:
            pass
    bot.send_message(msg.chat.id, 'Хабарлама жіберілді ✅')

# Фото қосу (тек админге)
@bot.message_handler(content_types=['photo'])
def add_photo(message):
    if message.from_user.id != ADMIN_ID:
        return
    photos = load_json(PHOTOS_FILE)
    photo_id = message.photo[-1].file_id
    photos.setdefault('all', []).append(photo_id)
    save_json(PHOTOS_FILE, photos)
    bot.reply_to(message, 'Фото сақталды ✅')

# Видео қосу (тек админге)
@bot.message_handler(content_types=['video'])
def add_video(message):
    if message.from_user.id != ADMIN_ID:
        return
    videos = load_json(VIDEOS_FILE)
    video_id = message.video.file_id
    videos.setdefault('all', []).append(video_id)
    save_json(VIDEOS_FILE, videos)
    bot.reply_to(message, 'Видео сақталды ✅')

print('🤖 Бот сәтті іске қосылды!')
bot.polling(none_stop=True)
