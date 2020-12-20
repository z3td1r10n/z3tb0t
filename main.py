import config
import sqlite3
from aiogram import Bot, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from messages import Messages
import markups
import asyncio


messages = Messages()

bot = Bot(token=config.token)
loop = asyncio.get_event_loop()
dp = Dispatcher(bot, storage=MemoryStorage(), loop=loop)
dp.middleware.setup(LoggingMiddleware())
TEST_PRICE = types.LabeledPrice(label='Цена теста', amount=1)


# Преобразовние корзины из строки в словарь
def make_dict(text: str):
    if text[0] == ' ':
        text = text[1::]
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    temp = text.split()
    result = {}
    for product in temp:
        count = product.split('__')[1]
        product = product.split('__')[0]
        cursor.execute('''SELECT * FROM products WHERE name = ?''', (product,))
        price = cursor.fetchall()[0][2]
        result[product] = [count, price]
    return result


# Проверка на наличие пользователя в базе
def is_user_exist(usr_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id,))
        conn.commit()
        if cursor.fetchall() == []:
            return False
        else:
            return True
    except:
        return False


# Создание нового пользователя
def new_user(usr_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    print('new user \nid: {}'.format(usr_id))
    try:
        cursor.execute('DELETE FROM users WHERE _id = ?', (usr_id,))
    except:
        pass
    cursor.execute('''INSERT INTO users (_id, is_admin) VALUES (?, 0)''', (usr_id,))
    conn.commit()


# Смена имени пользователя
def change_name(usr_id, name):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET name = ? WHERE _id = ?''', (name, usr_id))
    conn.commit()


# добавление товара в корзину
def add_to_cart(usr_id, product_name, count=1):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE _id = ?''', (usr_id,))
    fetchall = cursor.fetchall()[0][3]
    if fetchall is None:
        cursor.execute('''UPDATE users SET basket = ? WHERE _id = ?''', (' ' + product_name + f'__{count}', usr_id))
    else:
        if product_name in fetchall:
            exist_count = fetchall.split(product_name + '__')[1].split(' ')[0]
            fetchall = fetchall.replace(product_name + '__' + exist_count,
                                        product_name + '__' + str(int(exist_count) + count))
            cursor.execute('''UPDATE users SET basket = ? WHERE _id = ?''', (fetchall, usr_id))
        else:
            cursor.execute('''UPDATE users SET basket = ? WHERE _id = ?''',
                           ((fetchall + ' ' + product_name + f'__{count}'), usr_id))
    conn.commit()


# удаление товара из корзины? если count не задан или задан как 0,
# в противном случае удаление уменьшение количества этого товара в корзине на count,
# в том числе на отрицательное число, т.е. добавление, но это не рекомендуется
def remove_from_cart(usr_id, product_name, count=0):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE _id = ?''', (usr_id,))
    fetchall = cursor.fetchall()[0][3]
    new_basket = 0
    if count == 0:
        cursor.execute('''UPDATE users SET basket = ? WHERE _id = ?''', (new_basket, usr_id))
        exist_count = fetchall.split(product_name + '__')[1].split(' ')[0]
        fetchall.replace(' ' + product_name + '__' + exist_count, ' ')
    else:
        add_to_cart(usr_id, product_name, count=-count)


# удаление корзины
def remove_cart(usr_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET basket = ? WHERE _id = ?''', ('', usr_id))


# Удаление товара
def delete_product(product_name):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM products WHERE name = ?''', (product_name,))
    cursor.execute('''DROP TABLE {0}'''.format(product_name))
    cursor.execute('''DROP TABLE {0}'''.format(product_name + '_sold'))
    conn.commit()


# Удаление товаров
def delete_products(product_names):
    deleted = []
    undeleted = []
    if type(product_names) == str:
        try:
            delete_product(product_names)
            deleted.append(product_names)
        except:
            undeleted.append(product_names)
    else:
        for i in product_names:
            try:
                delete_product(i)
                deleted.append(i)
            except:
                undeleted.append(i)
    return [deleted, undeleted]


# Добавление товара(подразумевается подача на вход через тг только названия, типа(category), цены и фото товара
# , подача всех входных данных только через код)
def new_product(product_name: str,
                category: str = None,
                price: int = None,
                description: str = None,
                img_link: str = None):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO products (name) VALUES (?)''', (product_name,))
    cursor.execute('''CREATE TABLE {0} (key INTEGER PRIMARY KEY )'''.format(product_name))
    cursor.execute('''CREATE TABLE {0} (key INTEGER PRIMARY KEY )'''.format(product_name + '_sold'))
    if category is not None:
        cursor.execute('''UPDATE products SET category = ?  WHERE name = ?''', (category, product_name))
    if price is not None:
        cursor.execute('''UPDATE products SET price = ?  WHERE name = ?''', (price, product_name))
    if description is not None:
        cursor.execute('''UPDATE products SET description = ?  WHERE name = ?''', (description, product_name))
    if img_link is not None:
        cursor.execute('''UPDATE products SET img_link = ?  WHERE name = ?''', (img_link, product_name))
    conn.commit()


def is_admin(usr_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE name = ? AND is_admin = ?''', (usr_id, 1))
    if cursor.fetchall() is not None:
        return True
    else:
        return False


# Добавление ключей
def add_keys(product_name: str, keys: list):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    for key in keys:
        cursor.execute(f'''INSERT INTO {product_name} (key) VALUES (?)''', (key,))
    conn.commit()


# удаление ключей
def delete_keys(product_name: str, keys: list):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    for i in keys:
        try:
            cursor.execute('''DELETE FROM ? WHERE name = ?''', (product_name, i))
        except:
            cursor.execute('''DELETE FROM ?_sold WHERE name = ?''', (product_name, i))
    conn.commit()


# перенос ключей из таблицы активных в таблицу неактивных
def sell_keys(product_name: str, keys: list):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    for i in keys:
        cursor.execute('''DELETE FROM ? WHERE name = ?''', (product_name, i))
        cursor.execute('''INSERT INTO ?_sold (key) VALUES (?)''', (product_name, i))
    conn.commit()


def gen_catalog(price=None, category=None, product_name=None):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    if product_name is not None:
        cursor.execute('''SELECT * FROM products WHERE name LIKE '%{}%' '''.format(product_name))
    elif price is not None and category is not None:
        cursor.execute('''SELECT * FROM products WHERE price <= ? AND category = ?''', (price, category))
    elif price is not None:
        cursor.execute('''SELECT * FROM products WHERE price >= ? and price <= ?''', (price[0], price[1]))
    elif category is not None:
        cursor.execute('''SELECT * FROM products WHERE category = ?''', (category,))
    else:
        cursor.execute('''SELECT * FROM products''')

    markup = InlineKeyboardMarkup(row_width=2)
    for product in cursor.fetchall():
        button = InlineKeyboardButton((product[0] + ' — ' + str(product[2]) + ' руб.'), callback_data=product[0])
        markup = markup.add(button)
    conn.commit()
    return markup


# генерерирование инлайн клавиатуры для корзины
def gen_basket(products: dict):
    basket_markup = InlineKeyboardMarkup(resize_keyboard=True)
    names = list(products.keys())
    total_price = 0
    for i in range(len(products)):
        name = names[i]
        count, price = products[name]
        total_price += price
        remove = InlineKeyboardButton('Убрать', callback_data='rem_' + name)
        plus = InlineKeyboardButton('+', callback_data='+' + name)
        minus = InlineKeyboardButton('-', callback_data='-' + name)
        text = f'{name} - {str(price)} руб. х {str(count)}'
        info = InlineKeyboardButton(text, callback_data='show_' + name)
        basket_markup = basket_markup.add(info).row(remove, plus, minus)
    pay = InlineKeyboardButton('Оплатить ' + str(total_price), callback_data='pay_' + str(total_price))
    remove_all = InlineKeyboardButton('Очистить корзину', callback_data='rem_basket')
    return basket_markup.row(pay, remove_all)


# генерация корзины по id пользователя
def show_user_basket(usr_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id,))
    fetchall = cursor.fetchall()[0][3]
    if fetchall not in (None, '', ' '):
        products = make_dict(fetchall)
        markup = gen_basket(products)
        return markup
    else:
        text = messages.no_basket
        return text


def show_product(product_name):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM products WHERE name = ? LIMIT 1''', (product_name,))
    fetchall = cursor.fetchall()[0]
    price, description, img_link, in_stock = fetchall[2], fetchall[3], fetchall[4], fetchall[5]
    string = f'{product_name}\nЦена — {price}\nВ наличии: {in_stock}\n{description}'
    result = [string, img_link]
    return result


def logg_msg(usr_id, text):
    with open('logs.txt', 'w', encoding='UTF-8') as logs:
        logs.writelines(f'new message:\n'
                        f'from: {usr_id}\n'
                        f'text: {text}')


def logg(text):
    with open('logs.txt', 'w', encoding='UTF-8') as logs:
        logs.writelines(text)


async def send_product(usr_id, product_name):
    button_to_cart = InlineKeyboardButton('В корзину', callback_data=product_name)
    button_inline_catalog = InlineKeyboardButton('Каталог', callback_data='to_catalog')
    product = InlineKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    ).row(button_to_cart, button_inline_catalog)
    answer = show_product(product_name)
    img_link = answer[1]
    answer = answer[0]
    if img_link == '' or img_link is None:
        await bot.send_message(usr_id, answer)
    else:
        if '/' in img_link:
            with open(img_link, 'rb') as photo:
                await bot.send_photo(usr_id, photo=photo, caption=answer, reply_markup=product)
                await dp.current_state().set_state('product_watching')
        else:
            await bot.send_photo(usr_id, photo=img_link, caption=answer, reply_markup=product)
            await dp.current_state().set_state('product_watching')


def set_temp(usr_id, temp):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET temp = ? WHERE _id = ?''', (temp, usr_id))
    conn.commit()


def get_temp(usr_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE _id = ?''', (usr_id,))
    return cursor.fetchall()[0][4]


'''
пример обработки фото
@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(msg: types.Message):
    photo = msg.photo[0]['file_id']
    await bot.send_photo(msg.chat.id, photo)
    print(msg.caption)
'''


# получение текущего состояния бывает нужно для дебаггинга
@dp.message_handler(commands=["get_state"], state='*')
async def cmd_get_state(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    state = await dp.current_state().get_state()
    await bot.send_message(msg.chat.id, str(state))


@dp.message_handler(commands=["basket"], state='*')
async def cmd_basket(msg: types.Message):
    usr_id = msg.chat.id
    state = dp.current_state()
    answer = show_user_basket(usr_id)
    if type(answer) == str:
        await bot.send_message(usr_id, answer)
    else:
        mess_id = await bot.send_message(usr_id, 'Ваша корзина:', reply_markup=answer)
        set_temp(usr_id, mess_id)
        await state.set_state('basket')



@dp.callback_query_handler(lambda callback: callback.data != '#', state='basket')
async def callback_basket(callback: types.callback_query):
    data = str(callback.data)
    usr_id = callback.from_user.id
    if data.startswith('show_'):
        await send_product(usr_id, data[5::])
    elif data.startswith('rem_'):
        remove_from_cart(usr_id, data[4::])
        mess_id = get_temp(usr_id)
        new_basket = show_user_basket(usr_id)
        try:
            await bot.edit_message_text('Ваша корзина:', usr_id, mess_id, reply_markup=new_basket)
        except:
            await bot.edit_message_text('Ваша корзина пуста', usr_id, mess_id, reply_markup=markups.to_catalog)
    elif data.startswith('+'):
        add_to_cart(usr_id, data[4::], 1)
    elif data.startswith('-'):
        remove_from_cart(usr_id, data[4::], 1)
    elif data.startswith('pay_'):
        pass  # TODO: оплата прямо здесь
    else:  # data = rem_basket'
        remove_cart(usr_id)
        await bot.send_message(usr_id, 'ваша корзина успешно очищена', reply_markup=markups.to_catalog)


@dp.message_handler(commands=["catalog"], state='*')
async def cmd_catalog(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    markup = gen_catalog()
    button_filters = InlineKeyboardButton('фильтры', callback_data='filters')
    markup = markup.add(button_filters)
    await dp.current_state().set_state('catalog')
    await bot.send_message(msg.chat.id, 'Выберите товар', reply_markup=markup)


@dp.callback_query_handler(lambda callback: callback.data == 'to_admin_panel', state='*')
async def callback_admin(callback: types.callback_query):
    await dp.current_state().set_state('admin_panel')
    await bot.send_message(callback.from_user.id, messages.choose_action, reply_markup=markups.admin_panel)


@dp.callback_query_handler(lambda callback: callback.data != '#', state='catalog')
async def callback_catalog(callback: types.callback_query):
    usr_id = callback.from_user.id
    if callback.data != 'filters':
        await send_product(usr_id, callback.data)
    else:
        await bot.send_message(usr_id, 'укажите фильтры', reply_markup=markups.catalog_filters)
        await dp.current_state().set_state('catalog_filters')


@dp.callback_query_handler(lambda callback: callback.data != '#', state='product_watching')
async def callback_product(callback: types.callback_query):
    state = dp.current_state()
    usr_id = callback.from_user.id
    if callback.data == 'to_catalog':
        markup = gen_catalog()
        button_filters = InlineKeyboardButton('фильтры', callback_data='filters')
        markup = markup.add(button_filters)
        await dp.current_state().set_state('catalog')
        await bot.send_message(usr_id, 'Выберите товар', reply_markup=markup)
        await state.set_state('catalog')
    else:
        add_to_cart(usr_id, callback.data)
        await bot.send_message(usr_id, 'вы успешно добавили товар в корзину\nпросмотреть — /basket')


@dp.callback_query_handler(lambda callback: callback.data != '#', state='add_description')
async def callback_description(callback: types.callback_query):
    state = dp.current_state()
    usr_id = callback.from_user.id
    if callback.data == 'new_product':
        await state.set_state('new_product')
        await bot.send_message(usr_id, messages.new_product, reply_markup=markups.to_admin_panel)
    elif callback.data == 'to_admin_panel':
        await state.set_state('admin_panel')
        await bot.send_message(usr_id, messages.choose_action, reply_markup=markups.admin_panel)


@dp.callback_query_handler(lambda callback: callback.data == 'catalog')
async def callback_catalog_handler(callback: types.callback_query):
    usr_id = callback.from_user.id
    markup = gen_catalog()
    button_filters = InlineKeyboardButton('фильтры', callback_data='filters')
    markup = markup.add(button_filters)
    await dp.current_state().set_state('catalog')
    await bot.send_message(usr_id, 'Выберите товар', reply_markup=markup)


@dp.message_handler(commands=["start"], state='*')
async def cmd_start(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    await bot.send_message(usr_id, 'выберите действие', reply_markup=markups.catalog_or_filter)
    state = dp.current_state(user=msg.from_user.id)
    new_user(usr_id)
    await state.set_state('name_entered')


@dp.message_handler(commands=["help"], state='*')
async def cmd_help(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    await bot.send_message(msg.chat.id, messages.help)


@dp.message_handler(commands=["search"], state='*')
async def cmd_search(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    state = dp.current_state()
    if msg.text == '/search':
        await state.set_state('search_product')
        await bot.send_message(usr_id, 'введите название')
    else:
        answer = gen_catalog(product_name=msg.text.split()[1])
        button_filters = InlineKeyboardButton('фильтры', callback_data='filters')
        await dp.current_state().set_state('product_watching')
        if answer is not None:
            await bot.send_message(msg.chat.id, 'резульаты поиска:',
                                   reply_markup=answer.row(button_filters, markups.button_inline_catalog))
        else:
            answer = InlineKeyboardMarkup(row_width=2)
            await bot.send_message(msg.chat.id, 'Ничего не найдено',
                                   reply_markup=answer.row(button_filters, markups.button_inline_catalog))


@dp.message_handler(commands=["help_admin"], state='*')
async def cmd_help(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    if is_admin(msg.chat.id):
        await bot.send_message(msg.chat.id, messages.help_admin)


@dp.message_handler(commands=["new_product"], state='*')
async def cmd_new_product(msg: types.Message):
    state = dp.current_state()
    usr_id = msg.chat.id
    logg_msg(usr_id, msg.text)
    if is_admin(usr_id):
        await state.set_state('new_product')
        await bot.send_message(usr_id, messages.new_product, reply_markup=markups.to_admin_panel)


@dp.message_handler(commands=["delete_product"], state='*')
async def cmd_delete_product(msg: types.Message):
    state = dp.current_state()
    usr_id = msg.chat.id
    logg_msg(usr_id, msg.text)
    if is_admin(usr_id):
        await state.set_state('delete_product')
        await bot.send_message(usr_id, messages.delete_product, reply_markup=markups.to_admin_panel)


@dp.message_handler(commands=["add_keys"], state='*')
async def cmd_add_keys(msg: types.Message):
    state = dp.current_state()
    usr_id = msg.chat.id
    logg_msg(usr_id, msg.text)
    await state.set_state('add_keys')
    await bot.send_message(usr_id, messages.add_keys, reply_markup=markups.to_admin_panel)


@dp.message_handler(commands=["delete_keys"], state='*')
async def cmd_delete_keys(msg: types.Message):
    state = dp.current_state()
    usr_id = msg.chat.id
    logg_msg(usr_id, msg.text)
    await state.set_state('delete_keys')
    await bot.send_message(usr_id, messages.delete_keys, reply_markup=markups.to_admin_panel)


@dp.message_handler(commands=["admin"], state='*')
async def cmd_admin(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    usr_id = msg.chat.id
    state = dp.current_state(user=msg.from_user.id)
    cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id,))
    is_admin = cursor.fetchall()[0][2]
    conn.commit()
    if msg.text == '/admin ' + config.adm_password:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute('''UPDATE users SET is_admin = ?  WHERE _id = ?''', (1, usr_id))
        conn.commit()
        print('new admin\nid: ' + str(usr_id))
        await state.set_state('admin_panel')
        await bot.send_message(usr_id, messages.choose_action, reply_markup=markups.admin_panel)
    elif is_admin and msg.text == '/admin panel':
        await state.set_state('admin_panel')
        await bot.send_message(usr_id, messages.choose_action, reply_markup=markups.admin_panel)


@dp.message_handler(state='admin_panel')
async def admin_panel(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    state = dp.current_state(user=msg.from_user.id)
    if msg.text == 'Добавить товар':
        await state.set_state('new_product')
        await bot.send_message(usr_id, messages.new_product, reply_markup=markups.to_admin_panel)
    elif msg.text == 'Удалить товары':
        await state.set_state('delete_product')
        await bot.send_message(usr_id, messages.delete_product, reply_markup=markups.to_admin_panel)
    elif msg.text == 'Добавить ключи к товару':
        await state.set_state('add_keys')
        await bot.send_message(usr_id, messages.add_keys, reply_markup=markups.to_admin_panel)
    elif msg.text == 'Удалить ключи товара':
        await state.set_state('delete_keys')
        await bot.send_message(usr_id, messages.delete_keys, reply_markup=markups.to_admin_panel)


@dp.message_handler(content_types=['photo'], state='new_product')
async def product_creation(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    if len(msg.caption.split()) > 3:
        name, category, price = msg.caption.split()[:3]
        description = ' '.join(msg.caption.split()[3:])
        if price.isdigit():
            price = int(price)
            img_link = msg.photo[0]['file_id']
            new_product(name, category=category, price=price, description=description, img_link=img_link)
            await bot.send_message(usr_id, f'Товар {name} успешно создан\n'
                                           f'Вы можете добавить ещё один товар, либо перейти в админ панель',
                                   reply_markup=markups.to_admin_panel)
        else:
            await bot.send_message(usr_id, 'Цена должна быть числом', reply_markup=markups.to_admin_panel)
    elif len(msg.caption.split()) == 3:
        name, category, price = msg.caption.split()[:3]
        if price.isdigit():
            price = int(price)
            img_link = msg.photo[0]['file_id']
            new_product(name, category=category, price=price, img_link=img_link)
            await bot.send_message(usr_id, f'Товар {name} успешно создан\n'
                                           f'Вы можете добавить ещё один товар, либо перейти в админ панель',
                                   reply_markup=markups.to_admin_panel)
        else:
            await bot.send_message(usr_id, 'Цена должна быть числом', reply_markup=markups.to_admin_panel)
    else:
        await bot.send_message(usr_id, 'Вы должны ввести как минимум 3 слова', reply_markup=markups.to_admin_panel)


@dp.message_handler(state='new_product')
async def new_product_handler(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    state = dp.current_state()
    if msg.text == 'Перейти в админ-панель':
        await state.set_state('admin_panel')
        await bot.send_message(msg.chat.id, messages.choose_action, reply_markup=markups.admin_panel)
    else:
        await bot.send_message(usr_id, 'что-то пошло не так')


@dp.message_handler(state='delete_product')
async def delete_product_handler(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    text = msg.text
    if len(text.split()) > 1:
        deleted, undeleted = delete_products(text.split('\n'))
        if deleted is not []:
            deleted = 'удалены товары: ' + ', '.join(deleted) + '\n'
        else:
            deleted = 'ни одного товара не удалено\n'
        if undeleted is not []:
            undeleted = 'не удалось удалить товары :' + ', '.join(undeleted) + '\n'
        else:
            undeleted = ''
        await bot.send_message(usr_id, f'{deleted}{undeleted}Вы можете продолжить либо перейти в админ панель',
                               reply_markup=markups.to_admin_panel)
    else:
        try:
            delete_product(text)
            await bot.send_message(usr_id, f'товар {msg.text} удалён, вы можете продолжить либо перейти в админ панель',
                                   reply_markup=markups.to_admin_panel)
        except:
            await bot.send_message(usr_id, f'не удалось удалить товар {msg.text}', reply_markup=markups.to_admin_panel)


@dp.message_handler(state='add_keys')
async def add_keys_handler(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    text = msg.text.split(' ')
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM products WHERE name = ?''', (text[0],))
    if cursor.fetchall() is not None:
        add_keys(text[0], text[1::])
        await bot.send_message(usr_id, f'К товару {text[0]} успешно добавлены ключи({len(text) - 1})')
    else:
        await bot.send_message(usr_id, f'Продукт  {text[0]} не найден')


@dp.message_handler(state='add_keys')
async def delete_keys_handler(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    text = msg.text
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM products WHERE name = ?''', (text[0],))
    if cursor.fetchall():
        delete_keys(text[0], text[1::])
        await bot.send_message(usr_id, f'Ключи({len(text) - 1}) к товару {text[0]} успешно удалены')
    else:
        await bot.send_message(usr_id, f'Продукт  {text[0]} не найден')


@dp.message_handler(state='name_entered')
async def name_entered(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    state = dp.current_state(user=msg.from_user.id)
    if msg.text == 'Фильтры':
        await state.set_state('choose_filter')
        await bot.send_message(usr_id, 'выберите фильтр', reply_markup=markups.catalog_filters)
        await dp.current_state().set_state('catalog_filters')
    elif msg.text == 'полный каталог':
        await state.set_state('catalog')
        markup = gen_catalog()
        await bot.send_message(msg.chat.id, 'Выберите товар', reply_markup=markup)


@dp.message_handler(state='catalog_filters')
async def catalog_filters(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    state = dp.current_state()
    if msg.text == 'полный каталог':
        await cmd_catalog(msg)
        await state.set_state('catalog')
    elif msg.text == 'цена':
        await state.set_state('price_filter')
        await bot.send_message(usr_id, 'укажите нижнюю и верхнюю границы цены через пробел')
    elif msg.text == 'тип':
        await state.set_state('category_filter')
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM products''')
        categories = []
        products = cursor.fetchall()
        for product in products:
            if product[1] not in categories:
                categories.append(product[1])
        markup = InlineKeyboardMarkup()
        for category in categories:
            button = InlineKeyboardButton(category, callback_data=category)
            markup = markup.add(button)
        await bot.send_message(usr_id, 'Выберите тип', reply_markup=markup)
    elif msg.text == 'Поиск по названию':
        await state.set_state('search_product')
        await bot.send_message(usr_id, 'введите название')


@dp.callback_query_handler(lambda callback: callback.data != '#', state='category_filter')
async def callback_category(callback: types.callback_query):
    usr_id = callback.from_user.id
    markup = gen_catalog(category=callback.data)
    button_filters = InlineKeyboardButton('фильтры', callback_data='filters')
    markup = markup.add(button_filters)
    await dp.current_state().set_state('catalog')
    await bot.send_message(usr_id, 'Результат', reply_markup=markup)


@dp.message_handler(state='price_filter')
async def filter_price_handler(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    usr_id = msg.chat.id
    state = dp.current_state()
    price1, price2 = msg.text.split()
    price1, price2 = int(price1), int(price2)
    markup = gen_catalog(price=[price1, price2])
    button_filters = InlineKeyboardButton('фильтры', callback_data='filters')
    markup = markup.add(button_filters)
    await state.set_state('catalog')
    await bot.send_message(usr_id, 'Выберите товар', reply_markup=markup)


@dp.message_handler(state='search_product')
async def search_handler(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    answer = gen_catalog(product_name=msg.text)
    button_filters = InlineKeyboardButton('фильтры', callback_data='filters')
    await dp.current_state().set_state('product_watching')
    if answer is not None:
        await bot.send_message(msg.chat.id, 'резульаты поиска:', reply_markup=answer.row(button_filters,
                                                                                         markups.button_inline_catalog))
    else:
        answer = InlineKeyboardMarkup(row_width=2)
        await bot.send_message(msg.chat.id, 'Ничего не найдено', reply_markup=answer.row(button_filters,
                                                                                         markups.button_inline_catalog))


@dp.message_handler()
async def wtf(msg: types.Message):
    logg_msg(msg.chat.id, msg.text)
    print('wtf')


if __name__ == '__main__':
    executor.start_polling(dp)
