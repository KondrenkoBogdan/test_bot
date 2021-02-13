import requests

url = f'https://api.telegram.org/bot1601883845:AAEQdi7K8r675hrursARRZYxZ_M-j_HEQ1E/sendMessage'
data = {
    'chat_id': 391796080,  # тут твои ид, вроде как это твой, но проверь
    'text': "<b>ALL OK</b>",
    'parse_mode': 'html'
}
requests.post(url, data=data) # отправка запроса