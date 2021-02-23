import requests

url = f'https://api.telegram.org/bot1601883845:AAHhUg8-cmdsyfACZ3kqx8U-xwFV9BfTQQU/sendMessage'
data = {
    'chat_id': 391796080,
    'text': "<b>Бот работает, все хорошо</b>",
    'parse_mode': 'html'
}
requests.post(url, data=data)
