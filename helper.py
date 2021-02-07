import re
import requests
import json
import datetime
import config
import pytz
import telebot
from telebot import types
import schedule
import time
import psycopg2

connection = psycopg2.connect(user="matt",
                              password="123456",
                              host="localhost",
                              database="testpython")
cursor = connection.cursor()

P_TIMEZONE = pytz.timezone(config.TIMEZONE)
TIMEZONE_COMMON_NAME = config.TIMEZONE_COMMON_NAME

URL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'

bot = telebot.TeleBot(config.TOKEN)


def main_menu(message, is_start):
    # КАК ДАДУТ ИНТЕРНЕТ ИЗМЕНИТЬ ???!!!
    _name = message.from_user.first_name
    _chat_login = message.from_user.username
    c_id = chat_id(message)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Посмотреть курс валют', callback_data='look_course'))
    keyboard.add(types.InlineKeyboardButton(text='Узнать погоду', callback_data='look_weather_main'))

    _mailing = get_mailing(c_id)

    if _mailing is None:
        chat = set_chat(c_id, _name, _chat_login, "start")
        keyboard.add(types.InlineKeyboardButton(text='Зарегестрироваться для рассылки', callback_data='start_reg'))
    else:
        chat = get_chat(c_id)
        keyboard.add(types.InlineKeyboardButton(text='Личный кабинет', callback_data='account'))
        if _mailing:
            keyboard.add(types.InlineKeyboardButton(text='Отписаться от рассылки', callback_data='mailing_refuse'))
        else:
            keyboard.add(types.InlineKeyboardButton(text='Подписаться на рассылку', callback_data='mailing_true'))
    if is_start:
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id, text=f"Доброе время суток, {chat[1]}, чем можем вам помочь ?", reply_markup=keyboard)
    else:
        bot.edit_message_text(f"Доброе время суток, {chat[1]}, чем можем вам помочь ?", c_id, message.id,
                              reply_markup=keyboard)


def set_new_name(message):
    c_id = chat_id(message)
    set_chat_name(c_id, message.text)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="В главное меню", callback_data="main_menu"))
    bot.delete_message(c_id, message.id)
    bot.send_message(c_id, f"Отличо, {message.text}, теперь мы будем обращаться к вам так !",
                     reply_markup=keyboard)


def set_name(message):
    c_id = chat_id(message)
    set_chat_name(c_id, message.text)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='mailing_true'))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='mailing_false'))
    bot.send_message(c_id, f"Отлично, {message.text}, хотите ли вы получать от нас рассылку погоды и курсов валют ?",
                     reply_markup=keyboard)


def look_weather_main(call):
    c_id = chat_id(call)
    keyboard = types.InlineKeyboardMarkup()
    _chat = get_chat(c_id)
    if _chat[6] is not None:
        keyboard.add(types.InlineKeyboardButton(text='У себя в городе', callback_data=f'weather-{_chat[6]}'))
        keyboard.add(types.InlineKeyboardButton(text='По названию города', callback_data='look_weather_name'))
        bot.edit_message_text("Выберите, где хотите посмотреть погоду", c_id, call.message.id, reply_markup=keyboard)
    else:
        c_id = chat_id(call)
        bot.edit_message_text("Введите название города в котором хотите узнать погоду", c_id, call.message.id)
        bot.register_next_step_handler(call.message, get_weather)


def mailing_true(call):
    c_id = chat_id(call)
    set_mailing(c_id, True)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Посмотреть курс валют', callback_data='look_course'))
    keyboard.add(types.InlineKeyboardButton(text='Узнать погоду', callback_data='look_weather_main'))
    keyboard.add(types.InlineKeyboardButton(text='В главное меню', callback_data='main_menu'))
    bot.edit_message_text("Отлично, рассылка проходит в 08:00 и 19:00 по Киеву.\n"
                          "Но вы в любой момент можете зайти просмотреть интересующую вас информация сами", c_id,
                          call.message.id,
                          reply_markup=keyboard)


def mailing_refuse(call):
    c_id = chat_id(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='mailing_false'))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='main_menu'))
    bot.edit_message_text('Вы действительно хотите отписатсья от рассылки ?', c_id, call.message.id,
                          reply_markup=keyboard)


def mailing_false(call):
    c_id = chat_id(call)
    set_mailing(c_id, False)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Посмотреть курс валют', callback_data='look_course'))
    keyboard.add(types.InlineKeyboardButton(text='Узанть погоду', callback_data='look_weather_main'))
    keyboard.add(types.InlineKeyboardButton(text='Подписаться на рассылку', callback_data='mailing_true'))
    bot.edit_message_text("Ну как хош...\nЕсли что, ты всегда можешь поменять свой выбор.", c_id, call.message.id,
                          reply_markup=keyboard)


def load_exchange():
    return json.loads(requests.get(URL).text)


def get_exchange(ccy_key):
    for obj in load_exchange():
        if obj["ccy"] == ccy_key:
            return {"buy": obj["buy"], "sale": obj["sale"]}


def get_time():
    return str(datetime.datetime.now(P_TIMEZONE).strftime('%d.%m %H:%M:%S')) + f"( {TIMEZONE_COMMON_NAME} )"


def look_course(call):
    c_id = chat_id(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('USD', callback_data='get-USD'))
    keyboard.add(types.InlineKeyboardButton('EUR', callback_data='get-EUR'))
    keyboard.add(types.InlineKeyboardButton('RUR', callback_data='get-RUR'))
    bot.edit_message_text('Выберите с чем хотите сравнить',
                          c_id, call.message.message_id, reply_markup=keyboard)


def set_new_city_db(chat_id, city):
    city = city.replace("'", "")
    cursor.execute(
        f"UPDATE chat_test_second SET city = '{city}' WHERE chat_id = '{chat_id}'")
    connection.commit()


def set_new_city_func(message):
    c_id = chat_id(message)
    _res = find_weather_now(message.text)
    bot.delete_message(c_id, message.id)
    if _res['error']:
        error_worker(c_id, message, _res)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
        set_new_city_db(c_id, message.text)
        bot.send_message(c_id, text=f"Отлично, город {message.text} закреплен за вами. \n"
                                    f"Кстати, там сейчас {_res['temp']} градусов и "
                                    f"{config.get_weather_desription_by_id(_res['weather'][0])}.",
                         reply_markup=keyboard)


def account(message):
    c_id = chat_id(message)
    res = get_chat(c_id)
    _mailing = res[5]
    _city = res[6]
    _mailing_text = ""
    if _city is not None:
        _city_text = f"Ваш город {res[6]}"
    else:
        _city_text = f"Ваш город не указан"
    if _mailing:
        _mailing_text = "Вы подписаны на рассылку"
        _mailing_but = types.InlineKeyboardButton("Отписаться от рассылки", callback_data="mailing_false")
    else:
        _mailing_text = "Вы не подписаны на рассылку"
        _mailing_but = types.InlineKeyboardButton("Подписаться на рассылку", callback_data="mailing_true")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Изменить имя", callback_data="change_name"))
    keyboard.add(_mailing_but)
    keyboard.add(types.InlineKeyboardButton("Поставить новый город", callback_data="new_city"))
    keyboard.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
    bot.edit_message_text(f"Вы в личном кабинете:\nВаше имя: {res[1]}\n{_mailing_text}\n{_city_text}", c_id, message.id,
                          reply_markup=keyboard)


def find_weather_forecast(name):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={name}&units=metric&appid=267e0592bf093a835ba1fffc762f9f70"
    response = json.loads(requests.get(url).text)

def find_weather_now(name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={name}&units=metric&appid=267e0592bf093a835ba1fffc762f9f70"
    response = json.loads(requests.get(url).text)
    if response['cod'] != 200:
        return {"error": True, "message": response['message']}
    else:
        weathers = []
        for i in response["weather"]:
            weathers.append(i['id'])
        return {"error": False,
                "temp": response['main']['temp'],
                "weather": weathers,
                'humidity': response['main']['humidity'],
                "wind": response["wind"]["speed"],
                "clouds": response['clouds']["all"],
                "city": f"{response['name']}, {response['sys']['country']}",
                "sunrise": time.strftime("%H:%M:%S", time.gmtime(response["sys"]["sunrise"])),
                "sunset": time.strftime("%H:%M:%S", time.gmtime(response["sys"]["sunset"])),
                "visibility": response["visibility"],
                "feels": response["main"]["feels_like"],
                "districts": [response["main"]["temp_min"], response["main"]["temp_max"]]}


def get_weather(message, call=None):
    c_id = chat_id(message)
    if call is not None:
        _data = call.data
        res = find_weather_now(_data[8:])
    else:
        res = find_weather_now(message.text)
    if res['error']:
        error_worker(c_id, message, res)
    else:
        _weather_text = ""
        if len(res['weather']) == 1:
            _weather_text = config.get_weather_desription_by_id(res['weather'][0])
        else:
            _weather_text = "Погода:"
            for i in res['weather']:
                _weather_text += f"\n   {config.get_weather_desription_by_id(i)}"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Вернуться в главное меню', callback_data=f'main_menu'))
        _text = f"В данный момент в {res['city']}" \
                f"\n{res['temp']} градусов (ощущается как {res['feels']})" \
                f"\nМестами темперетура от {res['districts'][0]} до {res['districts'][1]}" \
                f"\n{_weather_text}" \
                f"\nВетер: {res['wind']} метров в секунду" \
                f"\nВлажность: {res['humidity']} процентов" \
                f"\nОблачность: {res['clouds']} процентов" \
                f"\nВидимость: {res['visibility']} метров" \
                f"\nВосход солнца в {res['sunrise']}" \
                f"\nЗакат в {res['sunset']}"
        if call is not None:
            bot.edit_message_text(_text, c_id, message.id, reply_markup=keyboard)
        else:
            bot.delete_message(c_id, message.id)
            bot.send_message(c_id, text=_text, reply_markup=keyboard)


def look_weather(message):
    c_id = chat_id(message)
    _res = find_weather_now(message.text)
    if _res['error']:
        error_worker(c_id, message, _res)
    else:
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id, f"Отлично, {message.text} привязан к вам!")


def get_course(call):
    c_id = chat_id(call)
    _course = call.data[4:7]
    _res = get_exchange(_course)
    _s = float(_res['sale'])
    _b = float(_res['buy'])
    _is_update = len(call.data) > 7
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton('Обновить', callback_data=f'get-{_course}-' + json.dumps({'s': _s, 'b': _b})))
    keyboard.add(types.InlineKeyboardButton('Вернуться в главное меню', callback_data=f'main_menu'))
    _b_diff = ''
    _s_diff = ''
    if _is_update:
        _old_buy = float(json.loads(call.data[8:])['b'])
        _old_sale = float(json.loads(call.data[8:])['s'])
        if _old_buy != _b:
            _b_diff = _old_buy - _b
            if _b_diff > 0:
                _b_diff = f"( +{_b_diff} )"
            else:
                _b_diff = f"( {_b_diff} )"
        if _old_sale != _s:
            _s_diff = _old_sale - _s
            if _s_diff > 0:
                _s_diff = f"( +{_s_diff} )"
            else:
                _s_diff = f"( {_s_diff} )"
    _text = f"Курс <b>UAH => {_course}</b>\n\nПокупка:{_b} {_b_diff}\nПродажа:{_s} {_s_diff}"
    if len(call.data) > 7:
        _text += f"\n\nОбновлено {get_time()}"
    bot.edit_message_text(_text, c_id, call.message.message_id, reply_markup=keyboard, parse_mode="HTML")


def set_chat_name(chat_id, name):
    cursor.execute(f"UPDATE chat_test_second SET name = '{name}' WHERE chat_id = '{chat_id}'")
    connection.commit()
    chat = get_chat(chat_id)
    return chat


def get_chat(chat_id):
    cursor.execute(f"SELECT * FROM chat_test_second WHERE (chat_id='{chat_id}') LIMIT 1")
    res = cursor.fetchall()
    if len(res) != 0:
        return res[0]
    else:
        return None


def set_mailing(chat_id, bool):
    cursor.execute(f"UPDATE chat_test_second SET mailing = '{bool}' WHERE chat_id = '{chat_id}'")
    connection.commit()


def set_chat(chat_id, name, chat_login, position):
    is_already_exists = get_chat(chat_id)
    if is_already_exists is None:
        cursor.execute(f"INSERT INTO chat_test_second (chat_id, name, chat_login, position) "
                       f"VALUES('{chat_id}','{name}','{chat_login}','{position}')")
        connection.commit()
        chat = get_chat(chat_id)
        return chat
    else:
        return is_already_exists


def start_of_registration(message):
    c_id = chat_id(message)
    _chat = get_mailing(c_id)
    keyboard = types.InlineKeyboardMarkup()
    if _chat is not None:
        keyboard.add(types.InlineKeyboardButton(text='В главнео меню', callback_data='main_menu'))
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id, f"Вы уже зарегестрированный пользователь", reply_markup=keyboard)
    else:
        keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='name_yes'))
        keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='name_no'))
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id,  f"Начался процесс регистрации,"
                                f" вас зовут {message.from_user.first_name}?", reply_markup=keyboard)


def chat_id(i):
    try:
        return i.message.chat.id
    except:
        return i.chat.id


def get_mailing(c_id):
    cursor.execute(f"SELECT mailing FROM chat_test_second WHERE (chat_id = '{c_id}') LIMIT 1")
    res = cursor.fetchall()
    if len(res) > 0:
        return res[0][0]
    else:
        return None


def error_worker(c_id, message, _res):
    if _res["message"] == "city not found":
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id, "Данного места не найдено, попробуйте еще раз")
    else:
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id, f"Произошла ошибка попробуйте еще раз или позже. Сообщени ошибки {_res['message']}")
    bot.register_next_step_handler(message, look_weather)