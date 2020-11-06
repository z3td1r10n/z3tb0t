import config
import sqlite3
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token=config.token)
dp = Dispatcher(bot)

# подключение к БД, далее не комментируется
conn = sqlite3.connect("test.db")
cursor = conn.cursor()
# -----

# сброс всех таблиц и повторное их создание, необходимо только для отладки, в релизе убрать
try:
    cursor.execute('''DROP TABLE users''')
    cursor.execute('''DROP TABLE products''')
except:
    pass

cursor.execute('''CREATE TABLE users
                  (_id INTEGER PRIMARY KEY, state TEXT, name TEXT, is_admin INTEGER)
               ''')
cursor.execute('''CREATE TABLE products
(
    name TEXT PRIMARY KEY,
    category TEXT,
    price INTEGER,
    description TEXT,
    img_link TEXT,
    in_stock TEXT
)
''')
conn.commit()
# -----


# Функция, проверяющая наличие пользователя в базе.
def is_user_exist(usr_id):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id, ))
        if cursor.fetchall() == []:
            return False
        else:
            return True
    except:
        return False
    conn.commit()
#  -----


# Функция создания нового пользователя. Добавляет пользователя в базу данных. Состояние(state) по умолчанию — 'start'
def new_user(usr_id):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    print('new user \nid: {}'.format(usr_id))
    _id = usr_id
    state = 'start'
    cursor.execute('''INSERT INTO users (_id, state, is_admin) VALUES (?, ?, ?)''', (_id, state, 0))

    conn.commit()
#  -----


# функция для смены состояния(state) пользователя
def change_state(usr_id, state):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET state = ? WHERE _id = ?''', (state, usr_id))
    conn.commit()
#  -----


# функция для смены имени пользователя
def change_name(usr_id, name):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET name = ? WHERE _id = ?''', (name, usr_id))
    conn.commit()
#  -----


# Добавление товара(подразумевается подача на вход через тг только названия товара, подача всех входных данных только напрямую)
def create_product(product_name: str, category: str = None, price: int = None, description: str = None, img_link: str = None):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO products (name) VALUES (?)''', (product_name))
    cursor.execute('''CREATE TABLE {0} (key INTEGER)'''.format(product_name))
    cursor.execute('''CREATE TABLE {0} (key INTEGER)'''.format(product_name + '_sold'))
    if category != None:
        cursor.execute('''UPDATE products SET category = ?  WHERE name = ?''', (category, product_name))
    if price != None:
        cursor.execute('''UPDATE products SET price = ?  WHERE name = ?''', (price, product_name))
    if description != None:
        cursor.execute('''UPDATE products SET description = ?  WHERE name = ?''', (description, product_name))
    if img_link != None:
        cursor.execute('''UPDATE products SET img_link = ?  WHERE name = ?''', (img_link, product_name))
    conn.commit()
#  -----


# Удаление товара
def delete_product(product_name):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM products WHERE name = ?''', (product_name))
    cursor.execute('''DROP TABLE {0}'''.format(product_name))
    cursor.execute('''DROP TABLE {0}'''.format(product_name + '_sold'))
    conn.commit()
#  -----


# Редактирование товара
def edit_product(product_name: str, category: str = None, price: int = None, description: str = None, img_link: str = None):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    if category != None:
        cursor.execute('''UPDATE products SET category = ?  WHERE name = ?''', (category, product_name))
    if price != None:
        cursor.execute('''UPDATE products SET price = ?  WHERE name = ?''', (price, product_name))
    if description != None:
        cursor.execute('''UPDATE products SET description = ?  WHERE name = ?''', (description, product_name))
    if img_link != None:
        cursor.execute('''UPDATE products SET img_link = ?  WHERE name = ?''', (img_link, product_name))
    conn.commit()
#  -----


# Добавление ключей
def add_keys(product_name: str, keys: list):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    for i in keys:
        cursor.execute('''INSERT INTO ? (key) VALUES (?)''', (product_name, i))
    conn.commit()
#  -----


# удаление ключей
def delete_keys(product_name: str, keys: list):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    for i in keys:
        try:
            cursor.execute('''DELETE FROM ? WHERE name = ?''', (product_name, i))
        except:
            cursor.execute('''DELETE FROM ?_sold WHERE name = ?''', (product_name, i))
    conn.commit()
#  -----


# перенос ключей из таблицы активных в такблицу неактивных
def sell_keys(product_name: str, keys: list):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    for i in keys:
        cursor.execute('''DELETE FROM ? WHERE name = ?''', (product_name, i))
        cursor.execute('''INSERT INTO ?_sold (key) VALUES (?)''', (product_name, i))
    conn.commit()
#  -----


# Клавиатуры и кнопки

button_create_product = KeyboardButton('Добавить товар')
button_delete_product = KeyboardButton('Удалить товар')
button_catalog = KeyboardButton('перейти к каталогу')
button_filter_price = KeyboardButton('цена')
button_filter_category = KeyboardButton('тип')
button_search_product = KeyboardButton('Поиск по названию')
button_backtofilters = KeyboardButton('Вернуться к фильтрам')
button_category1 = KeyboardButton('Тип 1')
button_category2 = KeyboardButton('Тип 2')
button_category3 = KeyboardButton('Тип 3')

markup3 = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_create_product).add(button_delete_product)


markup_user = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_catalog)


markup_filters = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_filter_price).add(button_filter_category).add(button_search_product)

markup_backtofilters = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_backtofilters)

markup_categories = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_category1).add(button_category2).add(button_category3).add(button_backtofilters)


#  -----


# обработка начального сообщения.
@dp.message_handler(commands=["start"])
async def cmd_start(message):
    usr_id = message.chat.id  # Считывание id пользователя. В дальнейшем этот id записывется в БД, как _id
    new_user(usr_id)          # создается запись в БД о новом пользователе
    await bot.send_message(usr_id, 'Похоже, вы здесь впервые, введите имя, по которому к вам стоит обращаться')
    change_state(usr_id, 'enter_name')
#  -----


# обработка сообщений для админ панели
@dp.message_handler(commands=["admin"])
async def admin_panel(message):
    usr_id = message.chat.id
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id,))
    is_admin = cursor.fetchall()[0][3]
    cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id,))
    state = cursor.fetchall()[0][1]  # считывание состояния пользователя
    conn.commit()
    if is_admin:
        if state == 'admin_panel':
            await message.reply("Выберите действие", reply_markup=markup3)
    else:
        await bot.send_message(usr_id, 'Введите пароль')
        change_state(usr_id, 'enter_password')
#  -----

# основная функция бота, выполняется каждый раз, как пользователь отправляет сообщение
@dp.message_handler(content_types=["text"])
async def logic(msg: types.Message):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    usr_id = msg.from_user.id  # Считывание id пользователя. В дальнейшем этот id записывется в БД, как _id
    cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id,))
    state = cursor.fetchall()[0][1]  # считывание состояния пользователя

    if state == 'enter_name':
        name = msg.text
        change_name(usr_id, name)
        cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id,))
        print(cursor.fetchall())
        conn.commit()
        change_state(usr_id, 'name_entered')
        await bot.send_message(usr_id, 'выберите действие', reply_markup=markup_user)
    elif state == 'enter_password':
        if msg.text == config.adm_password:
            conn = sqlite3.connect("test.db")
            cursor = conn.cursor()
            cursor.execute('''UPDATE users SET is_admin = ?  WHERE _id = ?''', (1, usr_id))
            conn.commit()
            change_state(usr_id, 'admin_panel')
            print('new admin')
            print('id: ' + str(usr_id))
            await bot.send_message(usr_id, "Выберите действие", reply_markup=markup3)
        else:
            await bot.send_message(usr_id, 'wrong password')
    elif state == 'name_entered':
        if msg.text == 'перейти к каталогу':
            await bot.send_message(usr_id, 'Укажите фильтры', reply_markup=markup_filters)
            change_state(usr_id, 'choose_filters')
    elif state == 'choose_filters':
        if msg.text == 'цена':
            await bot.send_message(usr_id, 'введите диапозон цен через пробел в формате:\n200 800', reply_markup=markup_backtofilters)
            change_state(usr_id, 'filter_price')
        elif msg.text == 'тип':
            await bot.send_message(usr_id, 'Выберите тип товара', reply_markup=markup_categories)
            change_state(usr_id, 'choose_category')
        elif msg.text == 'поиск по названию':
            await bot.send_message(usr_id, 'Введите название', reply_markup=markup_backtofilters)
            change_state(usr_id, 'search_product')
#  -----

if __name__ == '__main__':
    executor.start_polling(dp)