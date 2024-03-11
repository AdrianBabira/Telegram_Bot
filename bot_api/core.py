import re
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from database.core import crud
from database.common.models import db_sqlite, User, History
from common_stuff import locales, currencies, steps
from telegram_api.common.bot_init import bot
from site_api.core import request_locations, request_hotels, hotel_address
from playhouse.shortcuts import model_to_dict
from bot_api.utils import translate, hotel_price
from datetime import datetime
from typing import Any

check_user_exist = crud.check_if_data_exists()
get_user_history = crud.retrieve()


def get_history_logs(msg: Message) -> str:
    """
    Read history logs, if any
    :param msg:
    :return:
    """
    chat_id = msg.chat.id
    history_logs = History.select().join(User).where(User.chat_id == chat_id)
    ret_values = ''
    for log in history_logs:
        log_time = str(log.date_time)
        log_time = log_time[:log_time.rfind('.')]
        ret_values += f'{log.event} > {log_time} > {log.search_result}\n'
    return ret_values


def history_log(msg: Message, text: str, values: str) -> None:
    """
    Create new history log
    :param msg:
    :param text:
    :param values:
    :return:
    """
    chat_id = msg.chat.id
    user = User.get(chat_id=chat_id)
    History.create(user=user, event=text, date_time=datetime.utcnow(),
                   search_result=values)


def check_user_in_db(msg: Message) -> bool:
    """
    Check if user exits
    :param msg:
    :return:
    """
    if check_user_exist(db_sqlite, User, chat_id=msg.chat.id):
        return True
    return False


def add_user_to_db(msg: Message) -> None:
    """
    Add user
    :param msg:
    :return:
    """
    chat_id = msg.chat.id
    lang = msg.from_user.language_code
    if lang != 'ru':
        lang = 'en'
    User.get_or_create(chat_id=chat_id, language=lang, action='0',
                       locale=locales[lang], currency=currencies[lang],
                       order='', destination_id='', destination_name='',
                       min_price='0', max_price='0', distance='0',
                       quantity='0', pictures_count=0,
                       date_from=datetime.utcnow(),
                       date_to=datetime.utcnow())


def compose_message(msg: Message, string: str) -> str:
    """
    Composee message for current user
    :param msg:
    :param string:
    :return:
    """
    user = User.get(User.chat_id == msg.chat.id)
    action = user.action
    message = translate(string+action, msg)
    if action == '2':
        currency = user.currency
        message += f'{currency}'
    return message


def is_input_correct(msg: Message) -> bool:
    """
    Checks the correctness of incoming messages as search parameters
    :param msg: Message
    :return: True if the message text is correct
    """
    user = User.get(User.chat_id == msg.chat.id)
    action = user.action
    msg = msg.text.strip()
    if action == '6':
        date_pattern = r'^\d{4}-\d{2}-\d{2} \d{4}-\d{2}-\d{2}$'
        if re.match(date_pattern, msg):
            return True
    if action == '5' and msg.isdigit() and 0 < int(msg) <= 10:
        return True
    elif (action == '4' and ' ' not in msg and msg.isdigit() and 0
          < int(msg) <= 20):
        return True
    elif (action == '3' and ' ' not in msg and
          msg.replace('.', '').isdigit()):
        return True
    elif (action == '2' and msg.replace(' ', '').isdigit() and
          len(msg.split()) == 2):
        return True
    elif action == '1' and msg.replace(' ', '').replace('-', '').isalpha():
        return True


def make_locations_array(msg: Message) -> dict:
    """
    Make locations list
    :param msg:
    :return:
    """
    data = request_locations(msg)
    if not data:
        return {'bad_request': 'bad_request'}
    try:
        locations = dict()
        if len(data.get('sr')) > 0:
            for item in data.get('sr'):
                if (item['type'] == 'CITY') or (item['type'] ==
                                                'NEIGHBORHOOD'):
                    location_name = item['regionNames']['fullName']
                    locations[location_name] = item['gaiaId']
        return locations
    except Exception as e:
        print(f'Could not parse hotel api response. {e}')


def exact_location(data: dict, loc_id: str) -> str:
    """
     gets the id of location and returns locations name from data
     :param data: dict Message
    :param loc_id: location id
    :return: location name
    """
    for loc in data['reply_markup']['inline_keyboard']:
        if loc[0]['callback_data'] == loc_id:
            return loc[0]['text']


def get_locations(msg: Message):
    """
    Create a menu with possible locations
    :param msg:
    :return:
    """
    if not is_input_correct(msg):
        bot.send_message(msg.chat.id, compose_message(msg, 'mistake_'))
    else:
        wait_msg = bot.send_message(msg.chat.id, translate('wait', msg))
        locations = make_locations_array(msg)
        bot.delete_message(msg.chat.id, wait_msg.id)
        if not locations or len(locations) < 1:
            bot.send_message(msg.chat.id, str(msg.text) + translate(
                'locations_not_found', msg))
        elif locations.get('bad_request'):
            bot.send_message(msg.chat.id, translate('bad_request', msg))
        else:
            menu = InlineKeyboardMarkup()
            for loc_name, loc_id in locations.items():
                menu.add(InlineKeyboardButton(
                    text=loc_name,
                    callback_data='code' + loc_id)
                )
            menu.add(InlineKeyboardButton(text=translate('cancel', msg),
                                          callback_data='cancel'))
            bot.send_message(msg.chat.id, translate('loc_choose', msg),
                             reply_markup=menu)


def extract_search_parameters(msg: Message) -> dict:
    """
    extracts users search parameters from redis database
    :param msg: Message
    :return: dict with search parameters
    """
    user = User.get(User.chat_id == msg.chat.id)
    params = model_to_dict(user)
    return params


def get_search_parameters(msg: Message) -> None:
    """
    fixes search parameters
    :param msg: Message
    :return: None
    """
    chat_id = msg.chat.id
    user = User.get(User.chat_id == msg.chat.id)
    action = user.action
    if not is_input_correct(msg):
        bot.send_message(chat_id, compose_message(msg, 'mistake_'))
    else:
        query = User.update(action=str(int(action) + 1)).where(
            User.chat_id == chat_id)
        query.execute()
        if action == '2':
            min_price, max_price = sorted(msg.text.strip().split(), key=int)
            attr = {steps[action + 'min']: min_price}
            query = User.update(attr).where(User.chat_id == chat_id)
            query.execute()
            attr = {steps[action + 'max']: max_price}
            query = User.update(attr).where(User.chat_id == chat_id)
            query.execute()
            bot.send_message(chat_id, compose_message(msg, 'question_'))
        elif action == '4':
            attr = {steps[action]: msg.text.strip()}
            query = User.update(attr).where(User.chat_id == chat_id)
            query.execute()
            get_pictures_output(msg)
        elif action == '6':
            date_from, date_to = msg.text.strip().split()
            attr = {steps[action + 'from']: date_from}
            query = User.update(attr).where(User.chat_id == chat_id)
            query.execute()
            attr = {steps[action + 'to']: date_to}
            query = User.update(attr).where(User.chat_id == chat_id)
            query.execute()
            begin_sorting(msg)
        else:
            attr = {steps[action]: msg.text.strip()}
            query = User.update(attr).where(User.chat_id == chat_id)
            query.execute()
            bot.send_message(chat_id, compose_message(msg, 'question_'))


def begin_sorting(msg: Message) -> None:
    """
    Start executing of commands
    :param msg:
    :return:
    """
    chat_id = msg.chat.id
    query = User.update(action='0').where(User.chat_id == chat_id)
    query.execute()
    hotels_list(msg)


def get_pictures_output(msg: Message) -> None:
    """
    Create menu and ask user to extract pictures or not.
    :param msg:
    :return:
    """
    menu = InlineKeyboardMarkup()
    menu.add(InlineKeyboardButton(
        text=translate('option_yes', msg),
        callback_data='pictures_yes')
    )
    menu.add(InlineKeyboardButton(
        text=translate('option_no', msg),
        callback_data='pictures_no')
    )
    bot.send_message(msg.chat.id, translate('question_5', msg),
                     reply_markup=menu)


def get_parameters_information(msg: Message) -> str:
    """
    generates a message with information about the current search parameters
    :param msg:
    :return: string like information about search parameters
    """
    parameters = extract_search_parameters(msg)
    sort_order = parameters['order']
    city = parameters['destination_name']
    currency = parameters['currency']
    message = (
        f"<b>{translate('parameters', msg)}</b>\n"
        f"{translate('city', msg)}: {city}\n"
    )
    if sort_order == "DISTANCE":
        price_min = parameters['min_price']
        price_max = parameters['max_price']
        distance = parameters['distance']
        message += f"{translate('price', msg)}: {price_min} - " \
                   f"{price_max} {currency}\n" \
                   f"{translate('max_distance', msg)}: {distance} " \
                   f"{translate('dis_unit', msg)}"
    return message


def hotels_list(msg: Message) -> None:
    """
    displays hotel search results in chat
    :param msg: Message
    :return: None
    """
    chat_id = msg.chat.id
    wait_msg = bot.send_message(chat_id, translate('wait', msg))
    params = extract_search_parameters(msg)
    hotels = get_hotels(msg, params)
    bot.delete_message(chat_id, wait_msg.id)
    if not hotels or len(hotels) < 1:
        bot.send_message(chat_id, translate('hotels_not_found', msg))
    elif 'bad_request' in hotels:
        bot.send_message(chat_id, translate('bad_request', msg))
    else:
        quantity = len(hotels)
        bot.send_message(chat_id, get_parameters_information(msg))
        bot.send_message(chat_id, f"{translate('hotels_found', msg)}: "
                                  f"{quantity}")
        hotels_names = []
        for hotel in hotels:
            bot.send_message(chat_id, hotel['description'])
            hotels_names.append(hotel['name'])
            if len(hotel['pictures_urls']) > 0:
                for img in hotel['pictures_urls']:
                    bot.send_photo(chat_id, photo=img)
        entered_command = ''
        if params['order'] == 'PRICE_LOW_TO_HIGH':
            entered_command = '/lowprice'
        elif params['order'] == 'RECOMMENDED':
            entered_command = '/recommended'
        elif params['order'] == 'DISTANCE':
            entered_command = '/bestdeal'
        hotels_string = ', '.join(hotels_names)
        history_log(msg, entered_command, hotels_string)


def generate_hotels_descriptions(hotels: dict, msg: Message) -> Any:
    """
    generate hotels description
    :param msg: Message
    :param hotels: Hotels information
    :return: list with string like hotel descriptions
    """
    hotels_info = []
    user = User.get(User.chat_id == msg.chat.id)
    for hotel in hotels:
        info = dict()
        message = (
            f"{translate('hotel', msg)}: {hotel.get('name')}\n"
            f"{translate('address', msg)}: {hotel.get('address')}\n"
            f"{translate('distance', msg)}: {hotel.get('distance')}\n"
            f"{translate('price', msg)}: {hotel['price']} {user.currency}\n"
        )
        info['description'] = message
        info['pictures_urls'] = hotel['pictures']
        info['name'] = hotel.get('name')
        hotels_info.append(info)
    return hotels_info


def get_hotels(msg: Message, parameters: dict) -> [list, None]:
    """
    calls the required functions to take and process the hotel data
    :param msg: Message
    :param parameters: search parameters
    :return: list with string like hotel descriptions
    """
    data = request_hotels(parameters)
    if 'bad_req' in data:
        return ['bad_request']
    data = structure_hotels_info(msg, data)
    if not data or len(data['results']) < 1:
        return None
    if parameters['order'] == 'DISTANCE':
        distance = float(parameters['distance'])
        quantity = int(parameters['quantity'])
        data = choose_best_hotels(data['results'], distance, quantity)
    else:
        data = data['results']
    data = generate_hotels_descriptions(data, msg)
    return data


def structure_hotels_info(msg: Message, data: dict) -> dict:
    """
    structures hotel data
    :param msg: Message
    :param data: hotel data
    :return: dict of structured hotel data
    """
    params = extract_search_parameters(msg)
    data = data.get('data', {}).get('propertySearch', {}).get('properties')
    hotels = dict()
    hotels['total_count'] = len(data)
    temp_hotels = []
    try:
        if hotels['total_count'] > 0:
            for cur_hotel in data:

                hotel = dict()
                hotel['id'] = cur_hotel.get('id')
                hotel['name'] = cur_hotel.get('name')
                hotel['price'] = hotel_price(cur_hotel)
                if not hotel['price']:
                    continue
                hotel['distance'] = cur_hotel.get(
                    'destinationInfo').get('distanceFromDestination').get(
                    'value', translate('no_information', msg))
                if hotel not in temp_hotels:
                    if params['order'] == 'DISTANCE':
                        if ((hotel['price'] >= int(params['min_price'])) and
                            (hotel['price'] <= int(params['max_price'])) and
                            (hotel['distance'] <= float(params['distance']))):
                            temp_hotels.append(hotel)
                    else:
                        temp_hotels.append(hotel)
            if params['order'] == 'DISTANCE':
                temp_hotels = sorted(temp_hotels, key=lambda x: x['price'])
            if len(temp_hotels) > int(params['quantity']):
                temp_hotels = temp_hotels[:int(params['quantity'])]
                hotels['total_count'] = len(temp_hotels)
            for hotel in temp_hotels:
                address_and_pictures = hotel_address(hotel['id'], msg)
                hotel['address'] = address_and_pictures['address']
                hotel['pictures'] = address_and_pictures['pictures']
            hotels['results'] = temp_hotels
        return hotels
    except Exception as e:
        print(f'Error in function {structure_hotels_info.__name__}: {e}')


def choose_best_hotels(hotels: list[dict], distance: float, limit: int) -> \
        list[dict]:
    """
    deletes hotels that have a greater distance from the city center than
    the specified one, sorts the rest by price
    in order increasing and limiting the selection
    :param limit: number of hotels
    :param distance: maximum distance from city center
    :param hotels: structured hotels' data
    :return: required number of best hotels
    """
    hotels = list(filter(lambda x: float(x["distance"]) <= distance, hotels))
    hotels = sorted(hotels, key=lambda k: k["price"])
    if len(hotels) > limit:
        hotels = hotels[:limit]
    return hotels
