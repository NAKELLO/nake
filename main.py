@dp.message_handler(content_types=types.ContentType.VIDEO)
async def save_kids_video(message: types.Message):
    logging.info(f"[VIDEO] Келді: user_id={message.from_user.id}, video={message.video.file_id if message.video else 'ЖОҚ'}")

    if message.chat.id in BLOCKED_CHAT_IDS:
        return

    # ЖАҢА АДМИН ID — КОРЕЙКА
    is_admin = message.from_user.id == 7047272652

    if not is_admin:
        await message.reply("🚫 Сізде видео жіберуге рұқсат жоқ.")
        return

    if not message.video:
        await message.reply("⚠️ Видео табылмады. Қайтадан жіберіп көріңіз.")
        return

    data = load_json(KIDS_VIDEOS_FILE)
    file_id = message.video.file_id
    if file_id not in data['all']:
        data['all'].append(file_id)
        save_json(KIDS_VIDEOS_FILE, data)
        await message.reply("✅ Детский видео сақталды.")
    else:
        await message.reply("ℹ️ Бұл видео бұрыннан бар.")
