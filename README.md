﻿Telegram Bot usage

1) Install packages from requirements.txt
2) Edit file settings.ini and enter here 
   your Telegram Bot token, and 
   X-RapidAPI-Key value from the site 
   https://rapidapi.com/apidojo/api/hotels4/
3) Run main.py

# Поиск отелей в Telegram

Этот бот позволяет быстро подбирать отели прямо в мессенджере Telegram по различным критериям поиска. 

## Особенности

Данный бот позволяет:
* подбирать отели по самой низкой или рекомендуемой цене;
* подбирать отели по лучшему соотношению цена/расстояние от центра города;  
* задавать количество выводимых отелей;  
* задавать диапазон цен.
* задавать количество фотографий отеля.
* бот не использует и не запрашивает никакие персональные данные.
* двуязычная поддержка, зависимая от `language_code` от Telegram Bot API. 
  Так же есть возможность принудительного изменения языка в независимости от `language_code` 

## Requirements

* Python 3.7+
* [pyTelegramBotAPI](https://github.com/python-telegram-bot/python-telegram-bot) – Python Telegram Bot API
* [requests](https://github.com/psf/requests) - библиотека requests

Вы можете установить все зависимости, выполнив следующую команду: `pip install -r requirements.txt`


## Команды бота

* `/start` - запуск бота, выполняется автоматически при подключении к боту.
* `/help` - список команд и их описание
* `/lowprice` - топ дешевых отелей
* `/recomended` - топ рекомендуемых отелей
* `/bestdeal` - лучшие предложения
* `/history` - история поиска
* `/settings` - меню с настройками  

## Как работать с ботом Hoteline

Список всех команд, поддерживаемых ботом, можно посмотреть по команде `/help`
Команда `/settings` показывает меню настроек, 

![Настройки](img/settings.png)

где вы можете выбрать язык поиска (по умолчанию соответствует значению `language_code` от Telegram Bot API),

![Выбор языка](img/languages.png)

или выбрать предпочтительную валюту из ("RUB", "USD", "EUR") (по умолчанию определяется значением `language_code`: 'ru': 'RUB', 'en': 'USD')

![Выбор валюты](img/currencies.png)

В качестве дат заселения и выселения из отеля устанавливаются текущий (то есть сегодняшний) и следующий (завтрашний) дни. 
Далее приведена инструкция по работе с ботом. При ошибочном вводе бот выведет соответствующее сообщение и попросит ввести значение повторно.

### Топ дешевых отелей

1. Введите команду `/lowprice`. Бот запросит город, в котором вы хотите искать отели.
2. Введите название населенного пункта. Бот выполнит запрос к hotels api и выведет список локаций, названия которых похожи на введенный город. 
   Если бот не найдет ни одну локацию, то необходимо ввести название города еще раз, возможно вы допустили ошибку при написании. 
   
Ответ на запрос "moscow":

![Локации](img/locations.png)
   
3. Выберите один из предложенных вариантов, наиболее подходящих вашему запросу.
4. Бот запросит количество отелей, которые вы хотите вывести в качестве результата. Введите количество отелей. 
5. Бот выполнит следующий запрос к hotels api и выведет список отелей с указанием названия, класса, цены, адреса и расстояния от центра.

Пример результата:
![Отель](img/hotel.png)


### Топ дорогих отелей

1. Для получения списка рекомендуемых отелей введите команду `/recommended`и выполните пункты 2 - 5 из инструкции выше для топа дешевых отелей

### Лучшие предложения

1. Введите команду `/bestdeal`. Бот запросит город, в котором вы хотите искать отели.
2. Введите название населенного пункта. Бот выполнит запрос к hotels api и выведет список локаций, названия которых похожи на введенный город. 
   Если бот не найдет ни одну локацию, то необходимо ввести название города еще раз, возможно вы допустили ошибку при написании.
3. Выберите один из предложенных вариантов, наиболее подходящих вашему запросу.
4. Бот запросит диапазон цен на отели. Введите два числа через пробел, где первое число это минимальная стоимость отеля, а второе — максимальная. 
5. Бот запросит максимальное расстояние от центра города до отеля. Введите число.
6. Бот запросит количество отелей, которые вы хотите вывести в качестве результата. Введите количество отелей. 
7. Бот выполнит следующий запрос к hotels api и выведет список отелей с указанием названия, класса, цены, адреса и расстояния от центра

### Рекомендации 

Название города должно состоять только из букв русского или английского алфавита и символа дефис.
Диапазон цен представляет собой два целых положительных числа, разделенных пробелом, написанных в одну строку.
Максимальное расстояние от центра города должно быть написано в виде положительного целого или вещественного числа.
Количество выводимых отелей — целое положительное число. Максимальное возможное количество - 20, при вводе числа больше 20, нужно ввести заново. 
Количество выводимых фотографий — целое положительное число. Максимальное возможное количество - 10, при вводе числа больше 10, нужно ввести заново. 