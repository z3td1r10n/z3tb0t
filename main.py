import config
import telebot
from telebot import types
import sqlite3

# подключение к БД, далее не комментируется
conn = sqlite3.connect("data.db")
cursor = conn.cursor()
# -----

# сброс всех таблиц и повторное их создание, необходимо только для отладки, в релизе убрать
try:
    cursor.execute('''DROP TABLE users''')
    cursor.execute('''DROP TABLE products''')
except:
    pass

cursor.execute('''CREATE TABLE users
                  (_id INTEGER PRIMARY KEY, state TEXT, name TEXT)
               ''')
cursor.execute('''CREATE TABLE products
(
    name TEXT,
    category TEXT,
    price INTEGER,
    description TEXT,
    img_link TEXT,
    in_stock TEXT
)
''')
conn.commit()
# -----

bot = telebot.TeleBot(config.token)  # токен тг бота

# класс, обозначающий пользователя, нигде не используется, можно убрать
class User:
    def __init__(self, usr_id, name):
        self.id = usr_id
        self.name = name
#  -----

# Функция, проверяющая наличие пользователя в базе.
def is_user_exist(usr_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id, ))
        if cursor.fetchall() == []:
            return False
        else:
            return True
    except:
        return False
#  -----

# Функция создания нового пользователя. Добавляет пользователя в базу данных. Состояние(state) по умолчанию — 'start'
def new_user(usr_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    print('new user \nid: {}'.format(usr_id))
    _id = usr_id
    state = 'start'
    cursor.execute('''INSERT INTO users (_id, state) VALUES (?, ?)''', (_id, state))

    conn.commit()
#  -----

# функция для смены состояния(state) пользователя
def change_state(usr_id, state):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET state = ? WHERE _id = ?''', (state, usr_id))
    conn.commit()
#  -----

# функция для смены имени пользователя
def change_name(usr_id, name):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET name = ? WHERE _id = ?''', (name, usr_id))
    conn.commit()
#  -----

# Добавление товара(подразумевается подача на вход через тг только названия товара, подача всех входных данных только напрямую)
def create_product(product_name: str, category: str = None, price: int = None, description: str = None, img_link: str = None):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO products (name) VALUES (?)''', (product_name))
    cursor.execute('''CREATE TABLE {0} (key INTEGER)'''.format(product_name))
    cursor.execute('''CREATE TABLE {0} (key INTEGER)'''.format(product_name + '_sold'))
    if category != None:
        cursor.execute('''UPDATE products SET category = ?  WHERE _id = ?''', (category))
    if price != None:
        cursor.execute('''UPDATE products SET price = ?  WHERE _id = ?''', (price))
    if description != None:
        cursor.execute('''UPDATE products SET description = ?  WHERE _id = ?''', (description))
    if img_link != None:
        cursor.execute('''UPDATE products SET img_link = ?  WHERE _id = ?''', (img_link))
    conn.commit()
#  -----


# Удаление товара
def delete_product(product_name):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM products WHERE name = ?''', (product_name))
    cursor.execute('''DROP TABLE {0}'''.format(product_name))
    cursor.execute('''DROP TABLE {0}'''.format(product_name + '_sold'))
    conn.commit()
#  -----


# Редактирование товара
def edit_product(product_name: str, category: str = None, price: int = None, description: str = None, img_link: str = None):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    if category != None:
        cursor.execute('''UPDATE products SET category = ?  WHERE _id = ?''', (category))
    if price != None:
        cursor.execute('''UPDATE products SET price = ?  WHERE _id = ?''', (price))
    if description != None:
        cursor.execute('''UPDATE products SET description = ?  WHERE _id = ?''', (description))
    if img_link != None:
        cursor.execute('''UPDATE products SET img_link = ?  WHERE _id = ?''', (img_link))
    conn.commit()
#  -----


# Добавление ключей
def add_keys(product_name: str, keys: list):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
#  -----


# удаление ключей

#  -----



# обработка начального сообщения.
@bot.message_handler(commands=["start"])
def cmd_start(message):
    usr_id = message.chat.id  # Считывание id пользователя. В дальнейшем этот id записывется в БД, как _id
    new_user(usr_id)          # создается запись в БД о новом пользователе
    bot.send_message(usr_id, 'Похоже, вы здесь впервые, введите имя, по которому к вам стоит обращаться')
    change_state(usr_id, 'enter_name')


# основная функция бота, выполняется каждый раз, как пользователь отправляет сообщение
@bot.message_handler(content_types=["text"])
def logic(message):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    usr_id = message.chat.id  # Считывание id пользователя. В дальнейшем этот id записывется в БД, как _id
    cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id,))
    state = cursor.fetchall()[0][1]  # считывание состояния пользователя
    if message.text == ('/admin ' + config.adm_password):
        change_state('admin_panel')
        # TODO: добавить товар/удалить товар/редактировать товар(добавить или удалить ключ(и),
        #  редактироовать название, описание и т.д.)/просмотреть список товаров(как пользователь или как админ)
    elif state == 'enter_name':
        name = message.text
        change_name(usr_id, name)
        cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id,))
        change_state('name_entered')
        print(cursor.fetchall())
    elif state == 'name_entered':
        pass


#  -----

if __name__ == '__main__':
    bot.polling(none_stop=True)
