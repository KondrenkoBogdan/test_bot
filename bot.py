import cherrypy
import telebot
import config
from helper import *

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
WEBHOOK_PORT = 443
WEBHOOK_LISTEN = '104.248.133.84'

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.TOKEN)

bot = telebot.TeleBot(config.TOKEN)

if config.ENV == config.p:
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


@bot.message_handler(commands=['check_db'])
def start_command(message):
    check_db(message)


@bot.message_handler(commands=['start'])
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
        send_error(f"🤷🏿‍♂️ Бот не понимает пользователя {c[2]}. Он вводил {message.text}")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    c_id = chat_id(call)
    data = call.data
    if data == "look_course":
        look_course(call)
    elif data == "delete_user":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="↩️ Назад", callback_data="main_menu"))
        bot.edit_message_text(f"ID клиента которого хотите удалить",
                              c_id, call.message.id, parse_mode="HTML", reply_markup=keyboard)
        bot.register_next_step_handler(call.message, delete_user)
    elif data == "events_today":
        print(requests.get("https://www.un.org/ru/sections/observances/international-days/").text)
    elif data == "feed_back":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="↩️ Назад", callback_data="main_menu"))
        bot.edit_message_text(f"✏️ Отправьте ваш отзыв, замечание или пожелание сюда, мы моментально его получим! 🛎",
                              c_id, call.message.id, parse_mode="HTML", reply_markup=keyboard)
        bot.register_next_step_handler(call.message, feed_back_menu)
    elif data == "start_reg":
        start_of_registration(call.message)
    elif data.startswith('sel-') or data.startswith('buy-') or data.startswith('uah-') or data.startswith('oth-'):
        _course = call.data[4:7]
        _type = None
        if _course == "RUR":
            _course_text = "🇷🇺RUR🇷🇺"
        elif _course == "EUR":
            _course_text = "🇪🇺EUR🇪🇺"
        else:
            _course_text = "🇺🇸USD🇺🇸"
        if data.startswith('sel-'):
            _text = f"💰Введите сколько <b>{_course_text}</b> вы хотите <b>продать</b> за <b>🇺🇦UAH🇺🇦</b>"
        elif data.startswith('buy-'):
            _text = f"💰Введите сколько <b>{_course_text}</b> вы хотите <b>купить</b> за <b>🇺🇦UAH🇺🇦</b>"
        elif data.startswith('uah-'):
            _text = f"💰Введите сколько <b>🇺🇦UAH🇺🇦</b> вы хотите <b>купить</b> за {_course_text}"
        else:
            _text = f"💰Введите сколько <b>🇺🇦UAH🇺🇦</b> вы хотите <b>продать</b> за {_course_text}"
        bot.edit_message_text(_text, c_id,
                              call.message.id, parse_mode="HTML")
        bot.register_next_step_handler(call.message, increment_course, data)
    elif data.startswith('converter_menu'):
        converter_menu(call)
    elif data.startswith('converter-'):
        converter(call)
    elif data.startswith('course-'):
        course_menu(call)
    elif data.startswith('get-'):
        get_course(call)
    elif data.startswith('forecast-'):
        get_weather_forecast(call.message, call)
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
    elif call.data == "forecast_by_name":
        c_id = chat_id(call)
        bot.edit_message_text("🌤 Введите название города в котором хотите просмотреть прогноз на 7 дней", c_id, call.message.id)
        bot.register_next_step_handler(call.message, get_weather_forecast)
    elif call.data == "look_weather_by_name":
        c_id = chat_id(call)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
             types.InlineKeyboardButton(text='📆 Прогноз на 7 дней 📆', callback_data=f'forecast_by_name'))
        keyboard.add(
             types.InlineKeyboardButton(text='🌇 Погода сейчас 🌇', callback_data=f'look_weather_name'))
        keyboard.add(types.InlineKeyboardButton(text="↩️️ Назад", callback_data='look_weather_main'))
        bot.edit_message_text("🌤 Выберите, что хотите просмотреть", c_id, call.message.id,
                              reply_markup=keyboard)
    elif call.data == "look_weather_my_place":
        c_id = chat_id(call)
        keyboard = types.InlineKeyboardMarkup()
        _chat = get_chat(c_id)
        keyboard.add(
             types.InlineKeyboardButton(text='📆 Прогноз на 7 дней 📆', callback_data=f'forecast-{_chat[6]}'))
        keyboard.add(
             types.InlineKeyboardButton(text='🌇 Погода сейчас 🌇', callback_data=f'weather-{_chat[6]}'))
        keyboard.add(types.InlineKeyboardButton(text="↩️️ Назад", callback_data='look_weather_main'))
        bot.edit_message_text("🌤 Выберите, что хотите просмотреть", c_id, call.message.id,
                              reply_markup=keyboard)
    elif call.data == "look_weather_main":
        c_id = chat_id(call)
        keyboard = types.InlineKeyboardMarkup()
        _chat = get_chat(c_id)
        if _chat[6] is not None:
            keyboard.add(
                types.InlineKeyboardButton(text='🌇 У себя в городе 🌇', callback_data='look_weather_my_place'))
            keyboard.add(
                types.InlineKeyboardButton(text='🏙 По названию города 🏙', callback_data='look_weather_by_name'))
            keyboard.add(types.InlineKeyboardButton(text='↩️️ Назад️', callback_data='main_menu'))
            bot.edit_message_text("🌤 Выберите, где хотите посмотреть погоду", c_id, call.message.id,
                                  reply_markup=keyboard)
        else:
            keyboard.add(
                 types.InlineKeyboardButton(text='📆 Прогноз на 7 дней 📆', callback_data=f'forecast_by_name'))
            keyboard.add(
                 types.InlineKeyboardButton(text='🌇 Погода сейчас 🌇', callback_data=f'look_weather_name'))
            bot.edit_message_text("🌤 Выберите, что хотите просмотреть", c_id, call.message.id,
                                  reply_markup=keyboard)
    elif call.data == "look_weather_name":
        c_id = chat_id(call)
        bot.edit_message_text("🌤 Введите название города в котором хотите узнать погоду", c_id, call.message.id)
        bot.register_next_step_handler(call.message, get_weather)
    elif call.data == "change_name":
        bot.edit_message_text("🤚 Введите как к вам можно обращаться?", c_id, call.message.id)
        bot.register_next_step_handler(call.message, set_new_name)
    elif data.startswith('name_yes_'):
        set_name_yes(c_id, call.message, data[9:])
    elif call.data == "name_no":
        bot.send_message(c_id, "❓ Хорошо, тогда как вас зовут ?")
        bot.register_next_step_handler(call.message, set_name)
    elif call.data == "admin_panel":
        admin_panel(call)
    elif call.data == "mailing_all":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="В главное меню", callback_data="main_menu"))
        bot.edit_message_text(
            "📣 Напишите текст, этот текст будет <b>МОМЕНТАЛЬНО</b> разослан по <b>ВСЕМ</b> подписчикам",
            c_id, call.message.id, parse_mode="HTML",
            reply_markup=keyboard)
        bot.register_next_step_handler(call.message, mailing_all)
    elif call.data == "mailing":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="В главное меню", callback_data="main_menu"))
        bot.edit_message_text(
            "📣 Напишите текст, этот текст будет <b>МОМЕНТАЛЬНО</b> разослан по всем подписчикам у "
            "которых включена рыссылка", c_id, call.message.id, parse_mode="HTML",
            reply_markup=keyboard)
        bot.register_next_step_handler(call.message, mailing)
    elif call.data == "statistic":
        statistic(call)


def increment_course(message, data):
    c_id = chat_id(message)
    _course = data[4:7]
    _res = get_exchange(_course)
    _money_count = 0
    c = get_chat(c_id)
    try:
        _money_count = float(message.text)
    except:
        bot.send_message(c_id, text="Вы ввели не валидное число, попробуте еще раз."
                                    " Если Вы хотите ввести не целое число вводите его через точку\n"
                                    "❎ \"<s>20,50</s>\"\n"
                                    "✅ \"<b>20.50</b>\"", parse_mode="HTML")
        return bot.register_next_step_handler(message, increment_course, data)
    if data.startswith('buy-') or data.startswith('oth-'):
        _type = "sale"
    else:
        _type = "buy"
    if _course == "RUR":
        _course_text = "RUR🇷🇺"
    elif _course == "EUR":
        _course_text = "EUR🇪🇺"
    else:
        _course_text = "USD🇺🇸"
    _course_all_text = f"\n\n🏦 <b>Источник:</b> ПриватБанк 🏪\n\n⚖️ Покупка: {_res['buy']}\n⚖️ Продажа: {_res['sale']}"
    _increment = _res[_type]
    if data.startswith('sel-') or data.startswith('buy-'):
        _answer_money = _money_count * float(_increment)
    else:
        _answer_money = _money_count / float(_increment)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="⬅️ ️В главное меню", callback_data="main_menu"))
    keyboard.add(types.InlineKeyboardButton(text="↩️️ Назад", callback_data=f"converter-{_course}"))
    if data.startswith('sel-'):
        _text = f'Продавая <b>{config.zero_destroyer(_money_count)} {_course_text}</b>'\
                   f' Вы получите <b>{int(_answer_money)} UAH🇺🇦</b>'
    elif data.startswith('buy-'):
        _text = f"Покупая <b>{config.zero_destroyer(_money_count)} {_course_text}</b>"\
                   f" Вы отдадите <b>{int(_answer_money)} UAH🇺🇦</b>"
    elif data.startswith('uah-'):
        _text = f'Покупая <b>{config.zero_destroyer(_money_count)} UAH🇺🇦</b>'\
                f'Вы отдадите <b>{int(_answer_money)} {_course_text}</b>'
    else:
        _text = f'Продавая <b>{config.zero_destroyer(_money_count)} UAH🇺🇦</b>'\
                   f' Вы получите <b>{int(_answer_money)} {_course_text}</b>'
    _text += _course_all_text
    bot.send_message(c_id, _text, parse_mode="HTML", reply_markup=keyboard)
    send_error(f"🌪 Пользователь  {c[2]} использовал конвертер {data}")


def set_new_city_func(message):
    c_id = chat_id(message)
    _res = find_weather_now(message.text)
    if _res['error']:
        error_worker(c_id, message, _res, set_new_city_func)
    else:
        if _res['temp'] > 0:
            _weather_smile = "☀️"
        else:
            _weather_smile = "❄️"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("⬅️ В главное меню", callback_data="main_menu"))
        set_new_city_db(c_id, message.text)
        bot.send_message(c_id, text=f"🌇 Отлично, город <b>{message.text}</b> закреплен за вами. 🌇\n"
                                    f"{_weather_smile} Кстати, там сейчас <b>{_res['temp']}</b> градусов и "
                                    f"<b>{_res['weather'][0][1] + config.get_icon(_res['weather'][0][0])}.</b>",
                         reply_markup=keyboard, parse_mode="HTML")


def set_new_city_func_reg(message):
    c_id = chat_id(message)
    _res = find_weather_now(message.text)
    if _res['error']:
        error_worker(c_id, message, _res, set_new_city_func_reg)
    else:
        if _res['temp'] > 0:
            _weather_smile = "☀️"
        else:
            _weather_smile = "❄️"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='🔔 Да', callback_data='mailing_true'))
        keyboard.add(types.InlineKeyboardButton(text='🔕 Нет', callback_data='mailing_false'))
        set_new_city_db(c_id, message.text)
        bot.send_message(c_id, text=f"🌇 Отлично, город <b>{message.text}</b> закреплен за вами. 🌇\n"
                                    f"{_weather_smile} Кстати, там сейчас <b>{_res['temp']}</b> градусов и "
                                    f"<b>{_res['weather'][0][1] + config.get_icon(_res['weather'][0][0])}.</b>\n\n"
                                    f"🔔<b>Продолжим.</b> Хотите ли вы получать от нас рассылку с погодой Вашего города"
                                    f" и курсом гривны в 8:00 и 18:00 ?",
                         reply_markup=keyboard, parse_mode="HTML")


def get_weather_forecast(message, call=None):
    c_id = chat_id(message)
    c = get_chat(c_id)
    if call is not None:
        _city_name = call.data[9:]
    else:
        _city_name = message.text
    res = find_weather_seven(_city_name)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="↩️ В главное меню", callback_data="main_menu"))
    if call is not None:
        bot.edit_message_text(res, c_id, message.id, reply_markup=keyboard, parse_mode="HTML")
    else:
        bot.delete_message(c_id, message.id)
        bot.send_message(c_id, text=res, reply_markup=keyboard, parse_mode="HTML")
    send_error(f"🌪 Пользователь  {c[2]} просмотрел <b>ПРОГНОЗ</b> в <b>{_city_name}</b>.")


def get_weather(message, call=None):
    c_id = chat_id(message)
    if call is not None:
        _data = call.data
        res = find_weather_now(_data[8:])
    else:
        res = find_weather_now(message.text)
    c = get_chat(c_id)
    if res['error']:
        error_worker(c_id, message, res, get_weather)
    else:
        if res['temp'] > 0:
            _weather_smile = "☀️"
        else:
            _weather_smile = "❄️"
        _weather_text = ""
        if len(res['weather']) == 1:
            _weather_text = f"<b>{config.get_icon(res['weather'][0][0]) + res['weather'][0][1]}</b>"
        else:
            _weather_text = "🌤 Погода:"
            for i in res['weather']:
                _weather_text += f"\n<b>{config.get_icon(i[0]) + i[1]}</b>"
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
                f"\n💦 Влажность: <b>{res['humidity']}%</b>" \
                f"\n🌥 Облачность: <b>{res['clouds']}%</b>" \
                f"\n👁 Видимость: <b>{res['visibility']} метров</b>" \
                f"\n🌅 Восход солнца в <b>{res['sunrise']}</b>" \
                f"\n🌄 Закат в <b>{res['sunset']}</b>" \
                f"\n\n⏱ <i>Данные на {get_time()}</i>"
        if call is not None:
            bot.edit_message_text(_text, c_id, message.id, reply_markup=keyboard, parse_mode="HTML")
        else:
            bot.delete_message(c_id, message.id)
            bot.send_message(c_id, text=_text, reply_markup=keyboard, parse_mode="HTML")
        send_error(f"🌪 Пользователь  {c[2]} просмотрел погоду в <b>{res['city']}</b>.\n"
                   f"{_weather_smile} <b>{res['temp']}</b> градусов (ощущается как <b>{res['feels']}</b>){_district_text}")


def set_name_yes(c_id, message, name):
    set_chat_name(c_id, name)
    bot.edit_message_text(f"👍 Отлично, <b>{name}</b>, теперь я буду обращаться к вам так!\n🌍 А сейчас скажите мне "
                          f"названия вашего города.\n🌦 Я буду отслеживать там погоду и делиться этой информацией"
                          f" с <b>Вами</b>!", c_id, message.id, parse_mode="HTML")
    bot.register_next_step_handler(message, set_new_city_func_reg)


def set_name(message):
    c_id = chat_id(message)
    set_chat_name(c_id, message.text)
    bot.send_message(c_id,
                     f"👍 Отлично, <b>{message.text}</b>, теперь я буду обращаться к вам так!\n🌍 А сейчас скажите мне "
                     f"названия вашего города.\n🌦 Я буду отслеживать там погоду и делиться этой информацией"
                     f" с <b>Вами</b>!", parse_mode="HTML")
    bot.register_next_step_handler(message, set_new_city_func_reg)


def error_worker(c_id, message, _res, call_back):
    try:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('↩️ Вернуться в главное меню ↩️', callback_data=f'main_menu'))
        c = get_chat(c_id)
        if _res["message"] == "city not found":
            msg = bot.send_message(c_id, "🤷🏼 Данного места не найдено, попробуйте еще раз 🤷🏼",
                                   reply_markup=keyboard)
        else:
            msg = bot.send_message(c_id,
                                   f"Произошла ошибка попробуйте еще раз или позже. Сообщени ошибки {_res['message']}."
                                   f" Нам уже пришло уведомление об этом.",
                                   reply_markup=keyboard)
        bot.register_next_step_handler(msg, call_back)
        send_error(f"🆘 У пользователя  {c[1]}, {c[3]}, {c[2]} упала ошибка {_res}. Он вводил {message.text}")
    except:
        send_error(f"У ошибки - ошибка, я в шоке блин")

print(config.t)
print(config.t)
print(config.t)
print(config.ENV)
print(config.ENV)
print(config.ENV)
bot.remove_webhook()
if config.ENV == config.t:
    bot.polling(none_stop=True)
else:
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


