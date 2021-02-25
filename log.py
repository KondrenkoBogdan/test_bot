import requests

url = f'https://api.telegram.org/bot1637822207:AAEJDDtLzjWco27nV5JQDWSVP07k2Xsn86Y/sendMessage'
data = {
    'chat_id': 391796080,
    'text': "<b>Бот работает, все хорошо</b>",
    'parse_mode': 'html'
}
requests.post(url, data=data)
