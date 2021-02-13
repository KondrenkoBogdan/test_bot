import psycopg2
import telebot
from telebot import types
from helper import *
import telebot
import config
import datetime
import pytz
import json
import traceback
import schedule
import requests
import re
import credentials
import config
import logging
import cherrypy

import flask

connection = psycopg2.connect(user="galina_semenovna",
                              password="mitina777",
                              host="localhost",
                              database="bot_database")
cursor = connection.cursor()
cursor.execute(f"CREATE TABLE IF NOT EXISTS chat_test_second (id SERIAL PRIMARY KEY, name VARCHAR NOT NULL,"
               f" chat_id INT NOT NULL, chat_login VARCHAR NOT NULL, position VARCHAR, mailing BOOL,"
               f" city VARCHAR, lat FLOAT, lon FLOAT)")
connection.commit()

WEBHOOK_HOST = '104.248.133.84'
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '104.248.133.84'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.TOKEN)

bot = telebot.TeleBot(config.TOKEN)


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def start_command(message):
    main_menu(message, True)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def text(message):
    c_id = chat_id(message)
    if message.text == '/reg':
        start_of_registration(message)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='⬅️ В главнео меню', callback_data='main_menu'))
        bot.send_message(c_id, text="🤷🏼 Бот вас не понял", reply_markup=keyboard)
        c = get_chat(c_id)
        send_error(f"🤷🏿‍♂️ Бот не понимает пользователя {c[1]}, {c[2]}")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    c_id = chat_id(call)
    data = call.data
    if data == "look_course":
        look_course(call)
    elif data == "start_reg":
        start_of_registration(call.message)
    elif data.startswith('get-'):
        get_course(call)
    elif data.startswith('weather-'):
        get_weather(call.message, call)
    elif call.data == "mailing_false":
        mailing_false(call)
    elif call.data == "mailing_true":
        mailing_true(call)
    elif call.data == "mailing_refuse":
        mailing_refuse(call)
    elif call.data == "main_menu":
        main_menu(call.message, False)
    elif call.data == "account":
        account(call.message)
    elif call.data == "new_city":
        c_id = chat_id(call)
        bot.edit_message_text("🌃 Введите город который хотите закрепить за собой 🌃", c_id, call.message.id)
        bot.register_next_step_handler(call.message, set_new_city_func)
    elif call.data == "look_weather_main":
        c_id = chat_id(call)
        keyboard = types.InlineKeyboardMarkup()
        _chat = get_chat(c_id)
        if _chat[6] is not None:
            keyboard.add(
                types.InlineKeyboardButton(text='🌇 У себя в городе 🌇', callback_data=f'weather-{_chat[6]}'))
            keyboard.add(
                types.InlineKeyboardButton(text='🏙 По названию города 🏙', callback_data='look_weather_name'))
            keyboard.add(types.InlineKeyboardButton(text='⬅️ Назад ⬅️', callback_data='main_menu'))
            bot.edit_message_text("🌤 Выберите, где хотите посмотреть погоду", c_id, call.message.id,
                                  reply_markup=keyboard)
        else:
            c_id = chat_id(call)
            bot.edit_message_text("🌤 Введите название города в котором хотите узнать погоду", c_id,
                                  call.message.id)
            bot.register_next_step_handler(call.message, get_weather)
    elif call.data == "look_weather_name":
        c_id = chat_id(call)
        bot.edit_message_text("🌤 Введите название города в котором хотите узнать погоду", c_id, call.message.id)
        bot.register_next_step_handler(call.message, get_weather)
    elif call.data == "change_name":
        bot.edit_message_text("🤚 Введите как к вам можно обращаться?", c_id, call.message.id)
        bot.register_next_step_handler(call.message, set_new_name)
    elif call.data == "name_no":
        bot.send_message(c_id, "❓ Хорошо, тогда как вас зовут ?")
        bot.register_next_step_handler(call.message, set_name)
    elif call.data == "admin_panel":
        admin_panel(call)
    elif call.data == "mailing":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="В главное меню", callback_data="main_menu"))
        bot.edit_message_text(
            "📣 Напишите текст, этот текст будет <b>МОМЕНТАЛЬНО</b> разослан по всем подписчикам у "
            "которых включена рыссылка?", c_id, call.message.id, parse_mode="HTML",
            reply_markup=keyboard)
        bot.register_next_step_handler(call.message, mailing)
    elif call.data == "statistic":
        statistic(call)


def set_new_city_func(message):
    c_id = chat_id(message)
    _res = find_weather_now(message.text)
    bot.delete_message(c_id, message.id)
    if _res['error']:
        error_worker(c_id, message, _res)
    else:
        if _res['temp'] > 0:
            _weather_smile = "☀️"
        else:
            _weather_smile = "❄️"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("⬅️ В главное меню", callback_data="main_menu"))
        set_new_city_db(c_id, message.text)
        bot.send_message(c_id, text=f"🌇 Отлично, город {message.text} закреплен за вами. 🌇\n"
                                    f"{_weather_smile} Кстати, там сейчас {_res['temp']} градусов и "
                                    f"{config.get_weather_desription_by_id(_res['weather'][0])}.",
                         reply_markup=keyboard)


def get_weather(message, call=None):
    c_id = chat_id(message)
    if call is not None:
        _data = call.data
        res = find_weather_now(_data[8:])
    else:
        res = find_weather_now(message.text)
    c = get_chat(c_id)
    if res['error']:
        error_worker(c_id, message, res)
    else:
        if res['temp'] > 0:
            _weather_smile = "☀️"
        else:
            _weather_smile = "❄️"
        _weather_text = ""
        if len(res['weather']) == 1:
            _weather_text = f"<b>{config.get_weather_desription_by_id(res['weather'][0])}</b>"
        else:
            _weather_text = "🌤 Погода:"
            for i in res['weather']:
                _weather_text += f"\n<b>{config.get_weather_desription_by_id(i)}</b>"
        if res['districts'][0] == res['districts'][1]:
            _district_text = ""
        else:
            _district_text = f"\n🌡 Местами темперетура от <b>{res['districts'][0]} до {res['districts'][1]}</b>"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('🔄 Обновить 🔄', callback_data=f'weather-{res["city"]}'))
        keyboard.add(types.InlineKeyboardButton('⬅️ Вернуться в главное меню ⬅️', callback_data=f'main_menu'))
        _text = f"🌇 В данный момент в <b>{res['city']}</b>" \
                f"\n{_weather_smile} <b>{res['temp']}</b> градусов (ощущается как <b>{res['feels']}</b>)" \
                f"{_district_text}" \
                f"\n{_weather_text}" \
                f"\n💨 Ветер: <b>{res['wind']}</b> метров в секунду" \
                f"\n💦 Влажность: <b>{res['humidity']}</b> процентов" \
                f"\n🌥 Облачность: <b>{res['clouds']}</b> процентов" \
                f"\n👁 Видимость: <b>{res['visibility']}</b> метров" \
                f"\n🌅 Восход солнца в <b>{res['sunrise']}</b>" \
                f"\n🌄 Закат в <b>{res['sunset']}</b>" \
                f"\n\n⏱ <i>Данные на {get_time()}</i>"
        if call is not None:
            bot.edit_message_text(_text, c_id, message.id, reply_markup=keyboard, parse_mode="HTML")
        else:
            bot.delete_message(c_id, message.id)
            bot.send_message(c_id, text=_text, reply_markup=keyboard, parse_mode="HTML")
        send_error(f"🌪 Пользователь {c[1]}, {c[2]} просмотрел погоду в {res['city']}")


def look_weather(message):
    c_id = chat_id(message)
    _res = find_weather_now(message.text)
    if _res['error']:
        error_worker(c_id, message, _res)
    else:
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id, f"🌆 Отлично, {message.text} привязан к вам!")


def error_worker(c_id, message, _res):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('↩️ Вернуться в главное меню ↩️', callback_data=f'main_menu'))
    c = get_chat(c_id)
    if _res["message"] == "city not found":
        bot.delete_message(c_id, message.id)
        msg = bot.send_message(c_id, "🤷🏼 Данного места не найдено, попробуйте еще раз 🤷🏼",
                               reply_markup=keyboard)
    else:
        bot.delete_message(c_id, message.id)
        msg = bot.send_message(c_id,
                               f"Произошла ошибка попробуйте еще раз или позже. Сообщени ошибки {_res['message']}."
                               f" Нам уже пришло уведомление об этом.",
                               reply_markup=keyboard)
    bot.register_next_step_handler(msg, look_weather)
    send_error(f"🆘 У пользователя {c[1]}, {c[2]} упала ошибка {_res}")


bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

schedule.every().minute.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
