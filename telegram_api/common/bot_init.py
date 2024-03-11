import telebot
import configparser
from common_stuff import settings_path


config = configparser.ConfigParser()
config.read(settings_path)
token = config['CREDENTIALS']['token']
bot = telebot.TeleBot(token, parse_mode='HTML')
