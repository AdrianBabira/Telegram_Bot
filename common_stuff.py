import os


app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(app_path, r'database\local\hotels.db')
settings_path = os.path.join(app_path, r'settings.ini')
currencies = {
    "ru": "RUB",
    "en": "USD"
}
locales = {
    "ru": "ru_RU",
    "en": "en_US"
}
steps = {
    '1': 'destination_id',
    '2min': 'min_price',
    '2max': 'max_price',
    '3': 'distance',
    '4': 'quantity',
    '5': 'pictures_count',
    '6from': 'date_from',
    '6to': 'date_to'
}
