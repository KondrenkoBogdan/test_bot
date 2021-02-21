t = "TEST"
p = "PRODUCTION"
import time

ENV = t
if ENV == t:
    TOKEN = '1495508310:AAFBqWcsUwsMTUFRo01XGIzgYG4T_hT4q9U'  # test
else:
    TOKEN = '1670658089:AAGVaGq9hKX3cVbCxtM5PGhJMmhyU194m1A'  # prod
TIMEZONE = 'Europe/Kiev'
TIMEZONE_COMMON_NAME = 'Kiev, UA'


def zero_destroyer(num):
    _str = str(num)
    if _str.endswith("0"):
        _str = _str[:len(_str)-1]
        if _str.endswith("0") or _str.endswith("."):
            _str = zero_destroyer(_str)
    if _str.endswith("."):
        _str = _str[:len(_str)-1]
    return _str


def ave_from_num_array(arr):
    total_count = 0
    for i in arr:
        total_count += float(i)
    ave = total_count/len(arr)
    return ave


def get_day_by_unix(t):
    return time.strftime("%d.%m", time.gmtime(t))


def get_weather_desription_by_id(w_id):
    types = {
        200: "⛈ ",
        201: "⛈ ",
        202: "⛈ ",
        210: "⚡️ ",
        211: "⚡️ ",
        212: "⚡️ ",
        221: "⚡️ ",
        230: "⛈ ",
        231: "⛈ ",
        232: "⛈ ",

        300: "🌧 ",
        301: "🌧 ",
        302: "🌧 ",
        310: "🌧 ",
        311: "🌧 ",
        312: "🌧 ",
        313: "🌧 ",
        314: "🌧 ",
        321: "🌧 ",

        500: "🌧 ",
        501: "🌧 ",
        502: "🌧 ",
        503: "🌧 ",
        504: "🌧 ",
        511: "🌨 ",
        520: "🌧 ",
        521: "🌧 ",
        522: "🌧 ",
        531: "🌧 ",

        600: "🌨 ",
        601: "🌨 ",
        602: "🌨 ",
        611: "🌨 ",
        612: "🌨 ",
        613: "🌨 ",
        615: "🌨 ",
        616: "🌨 ",
        620: "🌨 ",
        621: "🌨 ",
        622: "🌨 ",

        701: "🌫 ",
        711: "🌫 ",
        721: "🌫 ",
        731: "💨 ",
        741: "🌫 ",
        751: "💨 ",
        761: "💨 ",
        762: "🌋 ",
        771: "🌫 ",
        781: "☄ ",

        800: "☀️ ",

        801: "☁️ ",
        802: "☁️ ",
        803: "☁️ ",
        804: "☁️ "
    }
    return types[w_id]
