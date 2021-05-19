import telebot
import config
from helper import get_mailing_clients, find_weather_now, load_exchange, mailing_weather, send_error
bot = telebot.TeleBot(config.TOKEN)
clients = get_mailing_clients()
keyboard = telebot.types.InlineKeyboardMarkup()
keyboard.add(telebot.types.InlineKeyboardButton(text="В главное меню", callback_data="main_menu"))
_index = 1
_success_mailing_text = ''
_unsubscribed_index = 0
_unsubscribed_users = ''


for c in clients:
    try:
        today_weather = mailing_weather(c[6], "mor")
        res = find_weather_now(c[6])
        if res['temp'] > 0:
            _weather_smile = "☀️"
        else:
            _weather_smile = "❄️"
        if res['districts'][0] == res['districts'][1]:
            _district_text = ""
        else:
            _district_text = f"\n🌡 Местами темперетура от <b>{res['districts'][0]} до {res['districts'][1]}</b>"
        _exchange = load_exchange()
        _course_text = "\n<b>Курс: 🇺🇦UAH🇺🇦 к:</b>"
        if len(res['weather']) == 1:
            _weather_text = f"<b>{config.get_icon(res['weather'][0][0]) + res['weather'][0][1]}</b>"
        else:
            _weather_text = "🌤 Погода:"
            for i in res['weather']:
                _weather_text += f"\n<b>{config.get_icon(i[0]) + i[1]}</b>"
        for i in _exchange:
            if i['ccy'] != "BTC":
                if i['ccy'] == "RUR":
                    _course_smile = "🇷🇺RUR🇷🇺"
                elif i['ccy'] == "EUR":
                    _course_smile = "🇪🇺EUR🇪🇺"
                else:
                    _course_smile = "🇺🇸USD🇺🇸"
                _course_text += f"\n   <b>{_course_smile}</b>" \
                                f"\n    <b>Покупка:</b> {float(i['buy'])}" \
                                f"\n    <b>Продажа:</b> {float(i['sale'])}"
        _text = f"🙋 Доброе утро, {c[1]}! 🌅" \
                f"\n🌇 В вашем городе <b>{c[6]}</b>" \
                f"\n\n<b>🌥 Прогноз на грядущий день</b>" \
                f"{today_weather}" \
                f"🌥 <b>Погода в данный момент</b>" \
                f"\n{_weather_smile} <b>{res['temp']}</b> градусов (ощущается как <b>{res['feels']}</b>)" \
                f"{_district_text}" \
                f"\n{_weather_text}" \
                f"\n💨 Ветер: <b>{res['wind']}</b> метров в секунду" \
                f"\n💦 Влажность: <b>{res['humidity']}</b> %" \
                f"\n🌥 Облачность: <b>{res['clouds']}</b> %" \
                f"\n👁 Видимость: <b>{res['visibility']}</b> метров" \
                f"\n{_course_text}" \
                f"\n\n<b>Мы желаем вам продуктивного дня и удачи!️</b>"
        bot.send_message(c[2], text=_text, reply_markup=keyboard, parse_mode="HTML")
        _success_mailing_text += f"\n<b>{_index}.</b> {c[2]}, {c[6]}"
        _index = _index + 1
    except:
        _unsubscribed_users += f"\n<b>{_unsubscribed_index + 1}.</b> {c[2]}, {c[6]}"
        _unsubscribed_index += 1

if _unsubscribed_index > 0:
    _unsubscribed_text = f"\n\n<b>Отписавшиеся пользователи</b>" \
                         f"\nКоличество {_unsubscribed_index}" \
                         f"{_unsubscribed_users}"
else:
    _unsubscribed_text = ''

send_error(f"<b>Утренняя рассылка прошла успешно !"
           f"\nБыло разосланно {len(clients)} сообщений</b>"
           f"\nИнформация о тех, кто получил сообщение:"
           f"{_success_mailing_text}"
           f"{_unsubscribed_text}")
