TOKEN = '1670658089:AAGVaGq9hKX3cVbCxtM5PGhJMmhyU194m1A' #prod
TIMEZONE = 'Europe/Kiev'
TIMEZONE_COMMON_NAME = 'Kiev, UA'


def get_weather_desription_by_id(w_id):
    types = {
        200: "🌧 Гроза с легким дождем",
        201: "🌧 Гроза с дождем",
        202: "🌧 Гроза с сильным дождем",
        210: "🌧 Легкая гроза",
        211: "🌧 Гроза",
        212: "🌧 Сильная гроза",
        221: "🌧 Переменная гроза",
        230: "🌧 Гроза с легкой моросью",
        231: "🌧 Гроза с моросью",
        232: "🌧 Гроза с сильной моросью",

        300: "🌧 Легкая морось",
        301: "🌧 Морось",
        302: "🌧 Сильная морось",
        310: "🌧 Легкий моросящий дождь",
        311: "🌧 Моросящий дождь",
        312: "🌧 Сильный моросящий дождь",
        313: "🌧 Ливень с изморосью",
        314: "🌧 Сильный ливень с изморосью",
        321: "🌧 Изморось",

        500: "🌧 Легкий дождь",
        501: "🌧 Умеренный дождь",
        502: "🌧 Сильный дождь",
        503: "🌧 Очень сильный дождь",
        504: "🌧 Пипец сильный дождь",
        511: "🌨 Дождь со снегом",
        520: "🌧 Слабый ливень",
        521: "🌧 Ливень",
        522: "🌧 Сильный ливень",
        531: "🌧 Пипец ливеняра",

        600: "🌨 Легкий снегопад",
        601: "🌨 Снегопад",
        602: "🌨 Сильный снегопад",
        611: "🌨 Мокрый снег",
        612: "🌨 Легкий дождь с мокрым снегом",
        613: "🌨 Сильный дождь с мокрым снегом",
        615: "🌨 Легкий дождь со снегом",
        616: "🌨 Дождь со снегом",
        620: "🌨 Слабый ливень со снегом",
        621: "🌨 Ливень со снегом",
        622: "🌨 Сильный ливень со снегом",

        701: "🌫 Легкий туман, пасмурно",
        711: "🌫 Смог",
        721: "🌫 Мгла",
        731: "🌫 Песочно-пылевая буря",
        741: "🌫 Туман",
        751: "🌫 Метет песок",
        761: "🌫 Метет пыль",
        762: "🌫 Вулканический пепел",
        771: "🌫 Шквалы",
        781: "☄ ️Торнадо",

        800: "☀️ Ясно",

        801: "☁️ Несколько облаков",
        802: "☁️ Рассеянные облака",
        803: "☁️ Облачно",
        804: "☁️ Пасмурные облака"
    }
    return types[w_id]
