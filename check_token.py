import telegram

# Укажи свой токен бота здесь
TOKEN = '7924945419:AAG7cqywFNBtN-Jichi2sk_ePJv_33gFUjQ'

# Попробуем получить информацию о боте
bot = telegram.Bot(token=TOKEN)

# Выводим информацию о боте
print(bot.get_me())
