from typing import Any
import requests
import configparser
from common_stuff import settings_path
from telebot.types import Message
from database.common.models import User
from bot_api.utils import translate
from playhouse.shortcuts import model_to_dict


config = configparser.ConfigParser()
config.read(settings_path)
api_key = config['CREDENTIALS']['X-RapidAPI-Key']
api_host = config['CREDENTIALS']['X-RapidAPI-Host']


def request_locations(msg: Message) -> Any:
    """
    Search for locations from the hotel api
    :param msg:
    :return:
    """
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host
    }
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    user = User.get(User.chat_id == msg.chat.id)
    loc = user.locale
    mtp = msg.text.strip()
    querystring = {"q": mtp, "locale": loc, }
    try:
        response = requests.request("GET", url, headers=headers,
                                    params=querystring, timeout=20)
        data = response.json()
        if data.get('message'):
            raise requests.exceptions.RequestException
        return data
    except requests.exceptions.RequestException as e:
        print(f'Server error: {e}')
    except Exception as e:
        print(f'Error: {e}')


def request_hotels(parameters: dict) -> Any:
    """
    request hotels information from the hotel api
    :param parameters: search parameters
    :return: response from hotel api
    """
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host
    }
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    result_size = int(parameters['quantity'])
    date_from = dict()
    date_from['year'] = int(parameters['date_from'][:4])
    date_from['month'] = int(parameters['date_from'][5:7])
    date_from['day'] = int(parameters['date_from'][8:])
    date_to = dict()
    date_to['year'] = int(parameters['date_to'][:4])
    date_to['month'] = int(parameters['date_to'][5:7])
    date_to['day'] = int(parameters['date_to'][8:])
    destination_structure = dict()
    destination_structure['regionId'] = parameters['destination_id']
    rooms = list()
    room = dict()
    room["adults"] = 1
    rooms.append(room)
    sorting_method = 'PRICE_LOW_TO_HIGH'
    if parameters['order'] == 'RECOMMENDED':
        sorting_method = 'RECOMMENDED'
    filters = dict()
    filters['availableFilter'] = 'SHOW_AVAILABLE_ONLY'
    if parameters['order'] == 'DISTANCE':
        price = dict()
        price['max'] = int(parameters['max_price'])
        price['min'] = int(parameters['min_price'])
        filters['price'] = price
        sorting_method = 'DISTANCE'
        result_size = 200
    payload = {
        "currency": parameters['currency'],
        "eapid": 1,
        "locale": parameters['locale'],
        "siteId": 300000001,
        "destination": destination_structure,
        "checkInDate": date_from,
        "checkOutDate": date_to,
        "rooms": rooms,
        "resultsStartingIndex": 0,
        "resultsSize": result_size,
        "sort": sorting_method,
        "filters": filters
    }
    print(f'Search parameters: {payload}')
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data.get('message'):
            raise requests.exceptions.RequestException
        return data
    except requests.exceptions.RequestException as e:
        print(f'Error receiving response: {e}')
        return {'bad_req': 'bad_req'}
    except Exception as e:
        print(f'Error in function {request_hotels.__name__}: {e}')
        return {'bad_req': 'bad_req'}


def hotel_address(hotel_id: str, msg: Message) -> dict:
    """
    returns hotel address and pictures
    :param hotel_id: str
    :param msg: Message
    :return: output_values
    :rtype: dict()
    """
    output_values = dict()
    user = User.get(User.chat_id == msg.chat.id)
    parameters = model_to_dict(user)
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host
    }
    url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"
    payload = {
        "currency": parameters['currency'],
        "eapid": 1,
        "locale": parameters['locale'],
        "siteId": 300000001,
        "propertyId": hotel_id
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data.get('message'):
            raise requests.exceptions.RequestException
        message = translate('no_information', msg)
        if data.get('data').get('propertyInfo').get('summary').get(
                'location').get('address').get('addressLine'):
            message = data.get('data').get('propertyInfo').get(
                'summary').get('location').get('address').get(
                'addressLine', message)
        output_values['address'] = message
        pictures = []
        if parameters['pictures_count'] > 0:
            pictures_counter = 0
            for item in data.get('data').get('propertyInfo').get(
                    'propertyGallery').get('images'):
                if pictures_counter < parameters['pictures_count']:
                    pictures.append(item.get('image').get('url'))
                    pictures_counter += 1
                else:
                    break
        output_values['pictures'] = pictures
        return output_values
    except requests.exceptions.RequestException:
        output_values['address'] = translate('no_information', msg)
        output_values['pictures'] = []
        return output_values
