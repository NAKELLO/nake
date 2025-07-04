from aiogram import Bot, Dispatcher, types, executor

bot = Bot(token='7748542247:AAFvfLMx25tohG6eOjnyEYXueC0FDFUJXxE')
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("✅ Бот жұмыс істеп тұр!")

if name == 'main':
    executor.start_polling(dp)
