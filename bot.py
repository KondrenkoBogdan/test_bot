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

connection = psycopg2.connect(user="matt",
                              password="123456",
                              host="localhost",
                              database="testpython")
cursor = connection.cursor()
cursor.execute(f"CREATE TABLE IF NOT EXISTS chat_test_second (id SERIAL PRIMARY KEY, name VARCHAR NOT NULL,"
               f" chat_id INT NOT NULL, chat_login VARCHAR NOT NULL, position VARCHAR, mailing BOOL,"
               f" city VARCHAR, lat FLOAT, lon FLOAT)")
bot = telebot.TeleBot(config.TOKEN)
connection.commit()


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


bot.polling(none_stop=True)
