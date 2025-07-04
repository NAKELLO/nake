@bot.message_handler(func=lambda m: m.text == '🎁 Бонус')
def check_bonus(message):
    user_id = str(message.from_user.id)
    bonus = load_json(BONUS_FILE)
    users = load_json(USERS_FILE)
    invited = users.get(user_id, {}).get('invited', [])
    ref_link = f'https://t.me/Darvinuyatszdaribot?start={user_id}'
    bot.send_message(message.chat.id,
                     f'🎁 Сізде {bonus.get(user_id, 0)} бонус бар.\n'
                     f'👥 Шақырған адам саны: {len(invited)}\n'
                     f'🔗 Сілтеме: {ref_link}')

@bot.message_handler(func=lambda m: m.text == '🛒 Сатып алу')
def buy(message):
    text = (
        '450 видеосы бар аралас – 500 тг\n'
        'Детский аралас – 1000 тг\n'
        'Чисто детский – 1500 тг + 2 канал бонус\n'
        '2000 тг – 5 канал\n'
        '2500 тг – 10 канал\n'
        '3000 тг – 20 канал (бәрін аласың)\n\n'
        'Жаз: @KazHubALU'
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == '👥 Қолданушылар саны')
def user_count(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_json(USERS_FILE)
    bot.send_message(message.chat.id, f'👥 Жалпы қолданушы саны: {len(users)}')

@bot.message_handler(func=lambda m: m.text == '📢 Хабарлама жіберу')
def admin_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, '✉️ Хабарламаны жазыңыз:')
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(msg):
    users = load_json(USERS_FILE)
    for user_id in users:
        try:
            bot.send_message(user_id, msg.text)
        except:
            pass
    bot.send_message(msg.chat.id, '✅ Хабарлама жіберілді!')

@bot.message_handler(content_types=['photo'])
def add_photo(message):
    if message.from_user.id != ADMIN_ID:
        return
    photos = load_json(PHOTOS_FILE)
    photo_id = message.photo[-1].file_id
    photos.setdefault('all', []).append(photo_id)
    save_json(PHOTOS_FILE, photos)
    bot.reply_to(message, '✅ Фото сақталды.')

@bot.message_handler(content_types=['video'])
def add_video(message):
    if message.from_user.id != ADMIN_ID:
        return
    videos = load_json(VIDEOS_FILE)
    video_id = message.video.file_id
    videos.setdefault('all', []).append(video_id)
    save_json(VIDEOS_FILE, videos)
    bot.reply_to(message, '✅ Видео сақталды.')

print("🤖 Бот іске қосылды!")
bot.polling(none_stop=True)
