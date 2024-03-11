from telebot.types import Message
from database.common.models import User
from datetime import datetime, timedelta


vocabulary = {
    'help': {
        'ru': (
            '<b>Команды бота</b>\n'
            '/help - список всех команд\n'
            '/lowprice - отели с низкими ценами\n'
            '/recommendedprice - рекомендуемые отели\n'
            '/bestdeal - лучшие предложения\n'
            '/history - история действий\n'
            '/settings - настройки\n'
        ),
        'en': (
            '<b>Bot commands</b>\n'
            '/help - list of all commands\n'
            '/lowprice - top cheap hotels\n'
            '/recommendedprice - top recommended hotels\n'
            '/bestdeal - best deals\n'
            '/history - user actions history\n'
            '/settings - settings\n'
        ),
    },
    'hello': {
        'ru': 'Привет. Рад приветствовать вас. Начните с команды /help.',
        'en': 'Hello, I\'m glad to welcome you here. Start with the'
              ' /help command.'
    },
    'mistake_1': {
        'ru': 'Некорректный ввод. Название города должно содержать только'
              ' буквы английского или русского алфавита и символ "-". '
              'Попробуйте ввести название еще раз.',
        'en': 'Invalid input. City name can contain only letters and the '
              'symbol "-". Try to enter the city name again.',
    },
    'mistake_2': {
        'ru': 'Некорректный ввод. Нужно ввести два положительных целых '
              'числа, разделенных пробелом. Пример "1000 2000". Повторите '
              'еще раз.',
        'en': 'Invalid input. You need to enter two positive integers '
              'separated by a space. Example: "10 20". Try again.'
    },
    'mistake_3': {
        'ru': 'Некорректный ввод. Нужно ввести положительное число. Пример:'
              ' "10" или "1.5". Повторите еще раз.',
        'en': 'Invalid input. Positive number must be entered. Example: "10"'
              ' or "1.5" Try again.'
    },
    'mistake_4': {
        'ru': 'Некорректный ввод. Число должно быть положительным, целым и '
              'не больше 20. Пример: "10". Повторите еще раз.',
        'en': 'Invalid input. Positive integer no more than 20 must be '
              'entered. Example: "10". Try again.'
    },
    'mistake_5': {
        'ru': 'Некорректный ввод. Число должно быть положительным, целым и '
              'не больше 10. Пример: "5". Повторите еще раз.',
        'en': 'Invalid input. Positive integer no more than 10 must be '
              'entered. Example: "5". Try again.'
    },
    'mistake_6': {
        'ru': 'Некорректный ввод. Формат ввода ГГГГ-ММ-ДД ГГГГ-ММ-ДД. Пример:'
              ' "2020-01-01 2020-01-05". Повторите еще раз.',
        'en': 'Invalid input. Input format should be YYYY-MM-DD YYYY-MM-DD. '
              'Example: "2020-01-01 2020-01-05". Try again.'
    },

    'question_1': {
        'ru': 'В каком городе искать отели?',
        'en': 'In which city to look for hotels?'
    },
    'question_2': {
        'ru': 'Введите диапазон цен через пробел ',
        'en': 'Enter the prices range separated by space '
    },
    'question_3': {
        'ru': 'Введите радиус поиска от центра города в км',
        'en': 'Enter the search radius from the city center in miles'
    },
    'question_4': {
        'ru': 'Сколько отелей вывести? Максимум - 20',
        'en': 'How many hotels to show? Maximum - 20'
    },
    'question_5': {
        'ru': 'Выводить фотографии отелей?',
        'en': 'Show hotels pictures?'
    },
    'question_6': {
        'ru': 'Введите дату заезда и отъезда через пробел в формате '
              'ГГГГ-ММ-ДД ГГГГ-ММ-ДД',
        'en': 'Enter checkIn and checkOut separated by space using '
              'format YYYY-MM-DD YYYY-MM-DD'
    },
    'pictures_question': {
        'ru': 'Сколько фотографий отеля вывести? Максимум - 10',
        'en': 'How many hotel pictures to show? Maximum - 10'
    },
    'locations_not_found': {
        'ru': '- по запросу ничего не найдено. Возможно вы допустили ошибку'
              ' в названии? Повторите еще раз.',
        'en': 'not found. Perhaps you made a mistake in the name? Try again.'
    },
    'hotels_not_found': {
        'ru': 'Отели не найдены. Попробуйте еще раз с другими параметрами.',
        'en': 'Hotels not found. Try again with another parameters.'
    },
    'hotel': {
        'ru': 'Отель',
        'en': 'Hotel'
    },
    'address': {
        'ru': 'Адрес',
        'en': 'Address'
    },
    'bad_request': {
        'ru': 'К сожалению, не могу получить ответ от сервера. Повторите '
              'поиск позже.',
        'en': 'Sorry, I could not get a response from the server, please '
              'try again later.'
    },
    'distance': {
        'ru': 'Расстояние до центра города',
        'en': 'Distance to city center',
    },
    'loc_choose': {
        'ru': 'Выберите город из списка',
        'en': 'Select the city from the list'
    },
    'loc_selected': {
        'ru': 'Выбрана локация',
        'en': 'Location selected'
    },

    'cancel': {
        'ru': 'Отмена',
        'en': 'Cancel'
    },
    'ask_to_select': {
        'ru': 'Выберите один из вариантов',
        'en': 'Select one of next options'
    },
    'current_language': {
        'ru': 'Текущий язык',
        'en': 'Current language'
    },
    'current_currency': {
        'ru': 'Текущая валюта',
        'en': 'Current currency'
    },
    'language': {
        'ru': 'Русский',
        'en': 'English'
    },
    'currency_': {
        'ru': 'Валюта',
        'en': 'Currency'
    },
    'language_': {
        'ru': 'Язык',
        'en': 'Language'
    },
    'canceled': {
        'ru': 'Отменено',
        'en': 'Canceled'
    },
    'hotels_found': {
        'ru': 'Найдено отелей',
        'en': 'Hotels found'
    },

    'misunderstanding': {
        'ru': 'Я вас не понимаю. Для ознакомления с командами бота '
              'напишите /help.',
        'en': 'I do not understand. To learn more about the bot commands '
              'enter /help'
    },
    'settings': {
        'ru': 'Настройки',
        'en': 'Settings'
    },
    'wait': {
        'ru': 'Пожалуйста, подождите\nЗапрашиваю информацию...',
        'en': 'Please, wait\nRequesting information...'
    },
    'parameters': {
        'ru': 'Параметры поиска',
        'en': 'Search parameters'
    },
    'rating': {
        'ru': 'Класс отеля',
        'en': 'Rating'
    },
    'city': {
        'ru': 'Город',
        'en': 'City'
    },
    'price': {
        'ru': 'Стоимость',
        'en': 'Price'
    },
    'max_distance': {
        'ru': 'Максимальное расстояние до центра города',
        'en': 'Maximum distance to city center'
    },
    'dis_unit': {
        'ru': 'км',
        'en': 'miles'
    },
    'no_information': {
        'ru': 'Нет данных',
        'en': 'No information'
    },
    'enter_command': {
            'ru': 'Пожалуйста, сначала введите нужную команду',
            'en': 'Please, first enter the command you want'
        },
    'option_yes': {
        'ru': 'Да',
        'en': 'Yes'
    },
    'option_no': {
        'ru': 'Нет',
        'en': 'No'
    },

}


def translate(key: str, msg: Message) -> str:
    """
    takes text in vocabulary in current language with key
    :param key: str key
    :param msg: Message
    :return: text of message from vocabulary
    """
    user = User.get(User.chat_id == msg.chat.id)
    lang = user.language
    return vocabulary[key][lang]


def check_in_n_out_dates(check_in: datetime = None,
                         check_out: datetime = None) -> dict:
    """
    Converts the dates of check-in and check-out into a string format,
    if no dates are specified, today and tomorrow are taken
    :param check_in: check-in date
    :param check_out: check-out date
    :return: dict with check-in and check-out dates
    """
    dates = {}
    if not check_in:
        check_in = datetime.now()
    if not check_out:
        check_out = check_in + timedelta(1)
    check_in_struct = dict()
    check_in_struct['day'] = check_in.day
    check_in_struct['month'] = check_in.month
    check_in_struct['year'] = check_in.year

    check_out_struct = dict()
    check_out_struct['day'] = check_out.day
    check_out_struct['month'] = check_out.month
    check_out_struct['year'] = check_out.year

    dates['check_in'] = check_in_struct
    dates['check_out'] = check_out_struct
    return dates


def hotel_price(hotel: dict) -> int:
    """
    return hotel price
    :param hotel: dict - hotel information
    :return: integer or float like number
    """
    price = 0
    try:
        price = hotel.get('price').get('lead').get('amount')
    except Exception as e:
        print(f'Hotel price getting error {e}')
    return price
