from bot import *

connection = psycopg2.connect(user="matt",
                              password="123456",
                              host="localhost",
                              database="testpython")

cursor = connection.cursor()


def get_chat(chat_id):
    cursor.execute()