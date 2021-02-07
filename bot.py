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
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(config.TOKEN)

app = flask.Flask(__name__)


# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@bot.message_handler(commands=['start'])
def start_command(message):
    main_menu(message, True)


@bot.message_handler(content_types=['text'])
def text(message):
    c_id = chat_id(message)
    if message.text == '/reg':
        start_of_registration(message)
    else:
        bot.send_message(c_id, text="Я тебя не понимаю")


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
        bot.edit_message_text("Введите город который хотите закрепить за собой !", c_id, call.message.id)
        bot.register_next_step_handler(call.message, set_new_city_func)
    elif call.data == "look_weather_main":
        look_weather_main(call)
    elif call.data == "look_weather_name":
        c_id = chat_id(call)
        bot.edit_message_text("Введите название города в котором хотите узнать погоду", c_id, call.message.id)
        bot.register_next_step_handler(call.message, get_weather)
    elif call.data == "change_name":
        bot.edit_message_text("Введите как к вам можно обращаться?", c_id, call.message.id)
        bot.register_next_step_handler(call.message, set_new_name)
    elif call.data == "name_no":
        bot.send_message(c_id, "Хорошо, тогда как вас зовут ?")
        bot.register_next_step_handler(call.message, set_name)
