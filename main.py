from database.common.models import init_database
from telegram_api.common.bot_init import bot
import telegram_api.core


init_database()
try:
    bot.polling(none_stop=True, interval=0)
except Exception as e:
    print(f'Unexpected error: {e}')
