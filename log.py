import requests
import config

url = f'https://api.telegram.org/bot{config.LOG_TOKEN}/sendMessage'
data = {
    'chat_id': 391796080,
    'text': "<b>Бот работает, все хорошо</b>",
    'parse_mode': 'html'
}
requests.post(url, data=data)
