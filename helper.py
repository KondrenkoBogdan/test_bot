import re
import requests
import json
import datetime
import config
import pytz
import telebot
from telebot import types
import time
import psycopg2

connection = psycopg2.connect(user="galina_semenovna",
                              password="mitina777",
                              host="localhost",
                              database="bot_database")
cursor = connection.cursor()

P_TIMEZONE = pytz.timezone(config.TIMEZONE)
TIMEZONE_COMMON_NAME = config.TIMEZONE_COMMON_NAME

URL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'

bot = telebot.TeleBot(config.TOKEN)


def main_menu(message, is_start):
    c_id = chat_id(message)
    keyboard = types.InlineKeyboardMarkup()
    _mailing = get_mailing(c_id)
    if _mailing is None:
        _name = message.chat.first_name
        _chat_login = message.chat.username
        chat = set_chat(c_id, _name, _chat_login)
        start_of_registration(message)
    else:
        chat = get_chat(c_id)
        keyboard.add(types.InlineKeyboardButton(text='📈 Курс валют', callback_data='look_course'))
        keyboard.add(types.InlineKeyboardButton(text='🧮 Конвертер валют', callback_data='converter_menu'))
        keyboard.add(types.InlineKeyboardButton(text='❄️ Узнать погоду ☀️', callback_data='look_weather_main'))
        keyboard.add(types.InlineKeyboardButton(text='👤 Личный кабинет ', callback_data='account'))
        keyboard.add(types.InlineKeyboardButton(text='🖋 Оставить отзыв или пожелание', callback_data='feed_back'))
    if chat[2] == 391796080:
        keyboard.add(types.InlineKeyboardButton(text='💻 Админка ⌨️', callback_data='admin_panel'))
    _text = f"👋 Доброе время суток, {chat[1]}\n❓ Чем можем вам помочь ?"
    if is_start:
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id, text=_text,
                         reply_markup=keyboard)
    else:
        bot.edit_message_text(_text, c_id, message.id,
                              reply_markup=keyboard)


def set_new_name(message):
    c_id = chat_id(message)
    set_chat_name(c_id, message.text)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="↩️ В главное меню", callback_data="main_menu"))
    bot.delete_message(c_id, message.id)
    bot.send_message(c_id, f"📩 Отличо, {message.text}, теперь мы будем обращаться к вам так !",
                     reply_markup=keyboard)


def feed_back_menu(message):
    c_id = chat_id(message)
    chat = get_chat(c_id)
    keyboard = types.InlineKeyboardMarkup()
    print(message)
    keyboard.add(types.InlineKeyboardButton(text="↩️ Вернуться в главнео меню", callback_data="main_menu"))
    send_error(f"☄️ <b>КЛИЕНТ ОСТАВИЛ ОТЗЫВ ИЛИ ПОЖЕЛАНИЕ</b> ☄️\n"
               f"Пользователь  <b>{chat[1]}, {chat[3]}, {chat[2]}</b>\n"
               f"Текст:\n<b>{message.text}</b>")
    bot.send_message(c_id, f"Большое спасибо, мы ценим ваше мнение и обязательно его учтем !", reply_markup=keyboard)


def mailing_all(message):
    clients = get_all_users()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="↩️ В главное меню", callback_data='main_menu'))
    for c in clients:
        bot.send_message(c[2], text=message.text, reply_markup=keyboard)


def mailing(message):
    clients = get_mailing_clients()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="↩️ В главное меню", callback_data='main_menu'))
    for c in clients:
        bot.send_message(c[2], text=message.text, reply_markup=keyboard)


def admin_panel(call):
    c_id = chat_id(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='📝 Создать рассылку ПО ВСЕМ', callback_data='mailing_all'))
    keyboard.add(types.InlineKeyboardButton(text='📝 Создать рассылку', callback_data='mailing'))
    keyboard.add(types.InlineKeyboardButton(text='📝 Статистика', callback_data='statistic'))
    keyboard.add(types.InlineKeyboardButton(text='↩️️ В главное меню', callback_data='main_menu'))
    bot.edit_message_text("Выберите, что хотите сделать", c_id, call.message.id, reply_markup=keyboard)


def mailing_true(call):
    c_id = chat_id(call)
    set_mailing(c_id, True)
    chat = get_chat(c_id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='📈 Курс валют', callback_data='look_course'))
    keyboard.add(types.InlineKeyboardButton(text='🧮 Конвертер валют', callback_data='converter_menu'))
    keyboard.add(types.InlineKeyboardButton(text='❄️ Узнать погоду ☀️', callback_data='look_weather_main'))
    keyboard.add(types.InlineKeyboardButton(text='↩️ В главное меню', callback_data='main_menu'))
    bot.edit_message_text("⏱ Отлично, рассылка проходит в 08:00 и 18:00 по Киеву.\n"
                          "Но вы в любой момент можете зайти просмотреть интересующую вас информация сами", c_id,
                          call.message.id,
                          reply_markup=keyboard)
    send_error(f"<b>ПОЛЬЗОВАТЕЛЬ ПОДПИСАЛСЯ НА РАССЫЛКУ</b>\n"
               f"{chat[1]}, {chat[3]}, {chat[2]}")


def mailing_refuse(call):
    c_id = chat_id(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='👍 Да', callback_data='mailing_false'))
    keyboard.add(types.InlineKeyboardButton(text='👎 Нет', callback_data='main_menu'))
    bot.edit_message_text('📧 Вы действительно хотите отписатсья от рассылки ?', c_id, call.message.id,
                          reply_markup=keyboard)


def mailing_false(call):
    c_id = chat_id(call)
    set_mailing(c_id, False)
    chat = get_chat(c_id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='📈 Курс валют', callback_data='look_course'))
    keyboard.add(types.InlineKeyboardButton(text='🧮 Конвертер валют', callback_data='converter_menu'))
    keyboard.add(types.InlineKeyboardButton(text='❄️ Узнать погоду ☀️', callback_data='look_weather_main'))
    keyboard.add(types.InlineKeyboardButton(text='🔔 Подписаться на рассылку 🔔', callback_data='mailing_true'))
    keyboard.add(types.InlineKeyboardButton(text='↩️ В главное меню ↩️', callback_data='main_menu'))
    bot.edit_message_text("🔕 <b>Рассылка прекращена</b>\n📣 Если что, Вы всегда можете поменять свой выбор.", c_id,
                          call.message.id,
                          reply_markup=keyboard, parse_mode="HTML")
    send_error(f"<b>ПОЛЬЗОВАТЕЛЬ ЗАПРЕТИЛ РАССЫЛКУ</b>\n"
               f"{chat[1]}, {chat[3]}, {chat[2]}")


def load_exchange():
    return json.loads(requests.get(URL).text)


def get_exchange(ccy_key):
    for obj in load_exchange():
        if obj["ccy"] == ccy_key:
            return {"buy": obj["buy"], "sale": obj["sale"]}


def get_time():
    return "<i>" + str(datetime.datetime.now(P_TIMEZONE).strftime('%d.%m.%y %H:%M')) + f" ({TIMEZONE_COMMON_NAME})</i>"


def look_course(call):
    c_id = chat_id(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('🇺🇸 USD 🇺🇸', callback_data='get-USD'))
    keyboard.add(types.InlineKeyboardButton('🇪🇺 EUR 🇪🇺', callback_data='get-EUR'))
    keyboard.add(types.InlineKeyboardButton('🇷🇺 RUR 🇷🇺', callback_data='get-RUR'))
    keyboard.add(types.InlineKeyboardButton(text='↩️️ Назад ↩️', callback_data='main_menu'))
    bot.edit_message_text('📊 Выберите с чем хотите сравнить 🇺🇦UAH🇺🇦',
                          c_id, call.message.message_id, reply_markup=keyboard)


def set_new_city_db(chat_id, city):
    city = city.replace("'", "")
    cursor.execute(
        f"UPDATE chat_test_second SET city = '{city}' WHERE chat_id = '{chat_id}'")
    connection.commit()


def account(message):
    c_id = chat_id(message)
    res = get_chat(c_id)
    _mailing = res[4]
    _city = res[5]
    _mailing_text = ""
    if _city is not None:
        _city_text = f"🌇 Ваш город <b>{res[5]}</b>"
    else:
        _city_text = f"🌇 Ваш город не указан"
    if _mailing:
        _mailing_text = "🔔 Вы <b>подписаны</b> на рассылку"
        _mailing_but = types.InlineKeyboardButton("🔕 Отписаться от рассылки", callback_data="mailing_false")
    else:
        _mailing_text = "🔕 Вы <b>не подписаны</b> на рассылку"
        _mailing_but = types.InlineKeyboardButton("🔔 Подписаться на рассылку", callback_data="mailing_true")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("✏️ Изменить имя", callback_data="change_name"))
    keyboard.add(_mailing_but)
    keyboard.add(types.InlineKeyboardButton("🌆 Поставить новый город", callback_data="new_city"))
    keyboard.add(types.InlineKeyboardButton("⬅️ В главное меню", callback_data="main_menu"))
    bot.edit_message_text(
        f"👤 <b>Вы в личном кабинете</b>\n📝 Ваше имя: <b>{res[1]}</b>\n{_mailing_text}\n{_city_text}", c_id,
        message.id,
        reply_markup=keyboard, parse_mode="HTML")


def find_weather_seven(name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={name}&units=metric&appid=267e0592bf093a835ba1fffc762f9f70&lang=ru"
    response = json.loads(requests.get(url).text)
    lat = response['coord']['lat']
    lon = response['coord']['lon']
    main_url = f"http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&units=metric&exclude=current,hourly,minutely,alerts&appid=267e0592bf093a835ba1fffc762f9f70&lang=ru"
    res = json.loads(requests.get(main_url).text)
    if response['cod'] != 200:
        return {"error": True, "message": response['message']}
    else:
        _text = f'🌆 <b>Прогноз на 7 дней в городе {name}</b> 👇\n\n'
        for i in res['daily']:
            _text += f'<b>⛅️ {config.get_day_by_unix(i["dt"])} {config.get_week_day_by_unix(i["dt"])} ' \
                     f'{i["weather"][0]["description"]} - {config.get_icon(i["weather"][0]["icon"])}</b>'
            _text += f'\n   🌡 Температур от <b>{round(float(i["temp"]["min"]))}</b> до <b>{round(float(i["temp"]["max"]))}</b>'
            _text += f'\n   🌅 Утром <b>{round(float(i["temp"]["morn"]))}</b> ощущается как <b>{round(float(i["feels_like"]["morn"]))}</b>'
            _text += f'\n   🌇 Днем <b>{round(float(i["temp"]["day"]))}</b> ощущается как <b>{round(float(i["feels_like"]["day"]))}</b>'
            _text += f'\n   🌃 Вечером <b>{round(float(i["temp"]["eve"]))}</b> ощущается как <b>{round(float(i["feels_like"]["eve"]))}</b>\n\n'
    return _text


def find_weather_now(name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={name}&units=metric&appid=267e0592bf093a835ba1fffc762f9f70&lang=ru"
    response = json.loads(requests.get(url).text)
    if response['cod'] != 200:
        return {"error": True, "message": response['message']}
    else:
        weathers = []
        for i in response["weather"]:
            weathers.append([i['icon'], i['description']])
        return {"error": False,
                "temp": round(float(response['main']['temp'])),
                "weather": weathers,
                'humidity': response['main']['humidity'],
                "wind": response["wind"]["speed"],
                "clouds": response['clouds']["all"],
                "city": f"{response['name']}, {response['sys']['country']}",
                "sunrise": time.strftime("%H:%M:%S", time.gmtime(response["sys"]["sunrise"]+7200)),
                "sunset": time.strftime("%H:%M:%S", time.gmtime(response["sys"]["sunset"]+7200)),
                "visibility": response["visibility"],
                "feels": round(float(response["main"]["feels_like"])),
                "districts": [round(float(response["main"]["temp_min"])), round(float(response["main"]["temp_max"]))]}


def converter_menu(call):
    c_id = chat_id(call)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('🇺🇸 USD 🇺🇸', callback_data='converter-USD'))
    keyboard.add(types.InlineKeyboardButton('🇪🇺 EUR 🇪🇺', callback_data='converter-EUR'))
    keyboard.add(types.InlineKeyboardButton('🇷🇺 RUR 🇷🇺', callback_data='converter-RUR'))
    keyboard.add(types.InlineKeyboardButton(text='↩️️ Назад ↩️', callback_data='main_menu'))
    bot.edit_message_text("👇 Выберите, что Вы хотите обменять", c_id, call.message.message_id,
                          reply_markup=keyboard, parse_mode="HTML")


def converter(call):
    c_id = chat_id(call)
    _course = call.data[10:13]
    if _course == 'RUR':
        _money_smile = "🇷🇺"
    elif _course == 'EUR':
        _money_smile = "🇪🇺"
    elif _course == 'USD':
        _money_smile = "🇺🇸"
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=f"{_money_smile} Купить {_course + _money_smile}",
                                            callback_data=f"buy-{_course}"))
    keyboard.add(types.InlineKeyboardButton(text=f"{_money_smile} Продать {_course + _money_smile}",
                                            callback_data=f"sel-{_course}"))
    keyboard.add(types.InlineKeyboardButton(text="↩️ Назад", callback_data=f"converter_menu"))
    bot.edit_message_text("👇 Выберите, что Вы хотите сделать", c_id, call.message.message_id,
                          reply_markup=keyboard, parse_mode="HTML")


def course_menu(call):
    c_id = chat_id(call)
    _course = call.data[7:10]
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="🧮 Использовать конвертер валют 🧮", callback_data=f"converter-{_course}"))
    keyboard.add(types.InlineKeyboardButton(text="📈 Посмотреть курс 📈", callback_data=f"get-{_course}"))
    keyboard.add(types.InlineKeyboardButton(text="↩️ Назад ↩️", callback_data=f"look_course"))
    bot.edit_message_text("👇 Выберите, что Вы хотите сделать", c_id, call.message.message_id,
                          reply_markup=keyboard, parse_mode="HTML")


def get_course(call):
    c_id = chat_id(call)
    chat = get_chat(c_id)
    send_error(f"💵 Пользователь  {chat[1]}, {chat[3]}, {chat[2]}, просмотрел курс {call.data[4:7]}")
    _course = call.data[4:7]
    _res = get_exchange(_course)
    _s = float(_res['sale'])
    _b = float(_res['buy'])
    _is_update = len(call.data) > 7
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton('🔄 Обновить 🔄', callback_data=f'get-{_course}-' + json.dumps({'s': _s, 'b': _b})))
    keyboard.add(types.InlineKeyboardButton('↩️ Вернуться в главное меню ↩️', callback_data=f'main_menu'))
    _b_diff = ''
    _s_diff = ''
    if _course == "RUR":
        _course_text = "RUR🇷🇺"
    elif _course == "EUR":
        _course_text = "EUR🇪🇺"
    else:
        _course_text = "USD🇺🇸"
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
    _text = f"📊 Курс <b>🇺🇦UAH => {_course_text}</b>\n\n⚖️ <b>Покупка: </b>{_b} {_b_diff}\n⚖️ <b>Продажа: </b>{_s} {_s_diff}\n\n🏦 <b>Источник:</b> ПриватБанк 🏪"
    if len(call.data) > 7:
        _text += f"\n\n⏱ <b>Обновлено: </b>{get_time()}"
    bot.edit_message_text(_text, c_id, call.message.message_id, reply_markup=keyboard, parse_mode="HTML")


def set_chat_name(chat_id, name):
    cursor.execute(f"UPDATE chat_test_second SET name = '{name}' WHERE chat_id = '{chat_id}'")
    connection.commit()
    chat = get_chat(chat_id)
    return chat


def get_total_count():
    cursor.execute(f"SELECT COUNT(*) FROM chat_test_second")
    response = cursor.fetchall()
    return response[0][0]


def get_mailing_clients():
    cursor.execute(f"SELECT * FROM chat_test_second WHERE (mailing=true)")
    response = cursor.fetchall()
    if len(response) != 0:
        res = []
        for i in response:
            res.append(i)
        return res
    else:
        return None


def get_registered_count():
    cursor.execute(f"SELECT COUNT(*) FROM chat_test_second WHERE (mailing is not null)")
    res = cursor.fetchall()
    if len(res) != 0:
        return res[0][0]
    else:
        return None


def get_subscribed_count():
    cursor.execute(f"SELECT COUNT(*) FROM chat_test_second WHERE (mailing = true)")
    res = cursor.fetchall()
    if len(res) != 0:
        return res[0][0]
    else:
        return None


def get_all_users():
    cursor.execute(f"SELECT * FROM chat_test_second")
    res = cursor.fetchall()
    if len(res) != 0:
        return res
    else:
        return None


def get_chat(chat_id):
    cursor.execute(f"SELECT * FROM chat_test_second WHERE (chat_id='{chat_id}') LIMIT 1")
    res = cursor.fetchall()
    if len(res) != 0:
        return res[0]
    else:
        return None


def statistic(call):
    c_id = chat_id(call)
    total_count = get_total_count()
    sub_count = get_subscribed_count()
    reg_count = get_registered_count()
    all_users = get_all_users()
    all_users_text = 'Спосок пользователей:'
    index = 1
    for u in all_users:
        if u[5] is None:
            _mailing_smile = "не зарегестрирован"
        elif u[5]:
            _mailing_smile = "🔔"
        else:
            _mailing_smile = "🔕"
        all_users_text += f"\n<b>{index}.</b> {u[1]}, {u[3]}, {u[2]}, {_mailing_smile}, {u[6]}"
        index += 1
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
    bot.edit_message_text(message_id=call.message.id, parse_mode="HTML", chat_id=c_id, reply_markup=keyboard,
                          text=f"<b>Всего</b> пользователей <b>{total_count}</b>"
                               f"\n<b>Зарегестрированных</b> пользователей <b>{reg_count}</b>"
                               f"\n<b>Пользователей</b> с подпиской <b>{sub_count}</b>"
                               f"\n{all_users_text}")


def set_mailing(chat_id, bool):
    cursor.execute(f"UPDATE chat_test_second SET mailing = '{bool}' WHERE chat_id = '{chat_id}'")
    connection.commit()


def set_chat(chat_id, name, chat_login):
    is_already_exists = get_chat(chat_id)
    if is_already_exists is None:
        cursor.execute(f"INSERT INTO chat_test_second (chat_id, name, chat_login) "
                       f"VALUES('{chat_id}','{name}','{chat_login}')")
        connection.commit()
        chat = get_chat(chat_id)
        _callback_text = f"🙋 <b>Новый пользователь\nИмя: {name}\nЛогин {chat_login}\nСhat_id {chat_id}\n" \
                         f"Порядковый номер {chat[0]}</b>"
        send_error(_callback_text)
        return chat
    else:
        return is_already_exists


def start_of_registration(message):
    c_id = chat_id(message)
    _chat = get_chat(c_id)
    keyboard = types.InlineKeyboardMarkup()
    print(_chat)
    if _chat[5] is not None and _chat[4] is not None:
        keyboard.add(types.InlineKeyboardButton(text='В главнео меню', callback_data='main_menu'))
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id, f"Вы уже зарегестрированный пользователь", reply_markup=keyboard)
    else:
        keyboard.add(types.InlineKeyboardButton(text='👍 Да', callback_data='name_yes_' + _chat[1]))
        keyboard.add(types.InlineKeyboardButton(text='👎 Нет', callback_data='name_no'))
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id, f"✏️ Начался процесс регистрации,"
                               f" вас зовут {_chat[1]}?", reply_markup=keyboard)


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


def send_error(message):
    url = f'https://api.telegram.org/bot1637822207:AAEJDDtLzjWco27nV5JQDWSVP07k2Xsn86Y/sendMessage'
    data = {
        'chat_id': 391796080,
        'text': message,
        'parse_mode': "html"
    }
    requests.post(url, data=data)
