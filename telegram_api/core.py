import telebot
import re
from telegram_api.common.bot_init import bot
from bot_api.core import check_user_in_db, add_user_to_db, \
    get_locations, compose_message, get_search_parameters, \
    exact_location, history_log, get_history_logs
from database.common.models import User
from telebot.types import Message, CallbackQuery
from bot_api.utils import translate


pattern = re.compile(r'/add[\s]([\w]+)[\s]([\w]+)')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: Message):
    """
    /start and /help bot commands
    :param message:
    :return:
    """
    if not check_user_in_db(message):
        add_user_to_db(message)
    if 'start' in message.text:
        bot.send_message(message.chat.id, translate('hello', message))
        history_log(message, '/start', '')
    else:
        bot.send_message(message.chat.id, translate('help', message))
        history_log(message, '/help', '')


@bot.message_handler(commands=['lowprice', 'recommended', 'bestdeal'])
def get_commands(message: Message):
    """
    /lowprice, /recommended and /bestdeal bot commands
    :param message:
    :return:
    """
    if not check_user_in_db(message):
        add_user_to_db(message)
    chat_id = message.chat.id
    query = User.update(action='1').where(User.chat_id == chat_id)
    query.execute()
    if 'lowprice' in message.text:
        query = User.update(order='PRICE_LOW_TO_HIGH').where(
            User.chat_id == chat_id)
        query.execute()
    elif 'recommended' in message.text:
        query = User.update(order='RECOMMENDED').where(
            User.chat_id == chat_id)
        query.execute()
    else:
        query = User.update(order='DISTANCE').where(
            User.chat_id == chat_id)
        query.execute()
    bot.send_message(chat_id, compose_message(message, 'question_'))


@bot.message_handler(commands=['history'])
def get_command_history(message: telebot.types.Message):
    """
    /history bot command
    :param message:
    :return:
    """
    logs = get_history_logs(message)
    bot.send_message(message.chat.id, logs)
    history_log(message, '/history', '')


@bot.message_handler(commands=['settings'])
def get_command_settings(message: Message) -> None:
    """
    "/settings" command handler, opens settings menu
    :param message: Message
    :return: None
    """
    if not check_user_in_db(message):
        add_user_to_db(message)
    menu = telebot.types.InlineKeyboardMarkup()
    menu.add(telebot.types.InlineKeyboardButton(text=translate("language_",
                                    message), callback_data='set_locale'))
    menu.add(telebot.types.InlineKeyboardButton(text=translate("currency_",
                                    message), callback_data='set_currency'))
    menu.add(telebot.types.InlineKeyboardButton(text=translate("cancel",
                                    message), callback_data='cancel'))
    bot.send_message(message.chat.id, translate("settings", message),
                     reply_markup=menu)
    history_log(message, '/settings', '')


@bot.callback_query_handler(func=lambda call: True)
def keyboard_handler(call: CallbackQuery) -> None:
    """
    buttons handlers
    :param call: CallbackQuery
    :return: None
    """
    chat_id = call.message.chat.id
    bot.edit_message_reply_markup(chat_id=chat_id,
                                  message_id=call.message.message_id)
    user = User.get(User.chat_id == chat_id)
    action = user.action
    if call.data.startswith('code'):
        if action != '1':
            bot.send_message(call.message.chat.id, translate(
                'enter_command', call.message))
            query = User.update(action='0').where(User.chat_id == chat_id)
            query.execute()
        else:
            loc_name = exact_location(call.message.json, call.data)
            destination_id = call.data[4:]
            destination_name = loc_name
            query = User.update(
                destination_id=destination_id,
                destination_name=destination_name
                ).where(User.chat_id == chat_id)
            query.execute()
            bot.send_message(
                chat_id,
                f"{translate('loc_selected', call.message)}: {loc_name}",
            )
            if user.order == 'DISTANCE':
                query = User.update(action='2').where(
                    User.chat_id == chat_id)
                query.execute()
            else:
                query = User.update(action='4').where(
                    User.chat_id == chat_id)
                query.execute()
            bot.send_message(chat_id, compose_message(call.message,
                                                      'question_'))

    elif call.data.startswith('pictures_'):
        if call.data == 'pictures_yes':
            bot.send_message(chat_id, translate('pictures_question',
                                                call.message))
        else:
            query = User.update(pictures_count=0).where(
                User.chat_id == chat_id)
            query.execute()
            query = User.update(action='6').where(
                User.chat_id == chat_id)
            query.execute()
            bot.send_message(chat_id, translate('question_6', call.message))
    elif call.data.startswith('set'):
        query = User.update(action='0').where(User.chat_id == chat_id)
        query.execute()
        menu = telebot.types.InlineKeyboardMarkup()
        if call.data == 'set_locale':
            menu.add(telebot.types.InlineKeyboardButton(text='Русский',
                                        callback_data='loc_ru_RU'))
            menu.add(telebot.types.InlineKeyboardButton(text='English',
                                        callback_data='loc_en_US'))
        elif call.data == 'set_currency':
            menu.add(telebot.types.InlineKeyboardButton(text='RUB',
                                        callback_data='cur_RUB'))
            menu.add(telebot.types.InlineKeyboardButton(text='USD',
                                        callback_data='cur_USD'))
            menu.add(telebot.types.InlineKeyboardButton(text='EUR',
                                        callback_data='cur_EUR'))
        menu.add(telebot.types.InlineKeyboardButton(text=translate(
            'cancel', call.message), callback_data='cancel'))
        bot.send_message(chat_id, translate('ask_to_select',
            call.message), reply_markup=menu)

    elif call.data.startswith('loc'):
        query = User.update(
            locale=call.data[4:],
            language=call.data[4:6]
        ).where(User.chat_id == chat_id)
        query.execute()
        bot.send_message(chat_id,
            f"{translate('current_language', call.message)}: "
            f"{translate('language', call.message)}")
    elif call.data.startswith('cur'):
        query = User.update(
            currency=call.data[4:]
        ).where(User.chat_id == chat_id)
        query.execute()
        bot.send_message(chat_id,
            f"{translate('current_currency', call.message)}: "
            f"{call.data[4:]}")
    elif call.data == 'cancel':
        query = User.update(action='0').where(User.chat_id == chat_id)
        query.execute()
        bot.send_message(chat_id, translate('canceled', call.message))


@bot.message_handler(content_types=['text'])
def get_text_messages(message: Message) -> None:
    """
    text messages handler
    :param message: Message
    :return: None
    """
    if not check_user_in_db(message):
        add_user_to_db(message)
    user = User.get(User.chat_id == message.chat.id)
    action = user.action
    if action == '0':
        pass
    elif action == '1':
        get_locations(message)
    elif action in ['2', '3', '4', '5', '6']:
        get_search_parameters(message)
    else:
        bot.send_message(message.chat.id, translate('misunderstanding',
                                                    message))


if __name__ == '__main__':
    bot.infinity_polling()
