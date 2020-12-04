import config
import sqlite3
from aiogram.types import input_file
from aiogram import Bot, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from messages import Messages
import markups

messages = Messages()

bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


# Функция, проверяющая наличие пользователя в базе.
def is_user_exist(usr_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id, ))
        conn.commit()
        if cursor.fetchall() == []:
            return False
        else:
            return True
    except:
        return False


# Функция создания нового пользователя. Добавляет пользователя в базу данных.
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


# функция для смены имени пользователя
def change_name(usr_id, name):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET name = ? WHERE _id = ?''', (name, usr_id))
    conn.commit()


# Удаление товара
def delete_product(product_name):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM products WHERE name = ?''', (product_name,))
    cursor.execute('''DROP TABLE {0}'''.format(product_name))
    cursor.execute('''DROP TABLE {0}'''.format(product_name + '_sold'))
    conn.commit()


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
    cursor.execute('''CREATE TABLE {0} (key INTEGER)'''.format(product_name))
    cursor.execute('''CREATE TABLE {0} (key INTEGER)'''.format(product_name + '_sold'))
    if category is not None:
        cursor.execute('''UPDATE products SET category = ?  WHERE name = ?''', (category, product_name))
    if price is not None:
        cursor.execute('''UPDATE products SET price = ?  WHERE name = ?''', (price, product_name))
    if description is not None:
        cursor.execute('''UPDATE products SET description = ?  WHERE name = ?''', (description, product_name))
    if img_link is not None:
        cursor.execute('''UPDATE products SET img_link = ?  WHERE name = ?''', (img_link, product_name))
    conn.commit()


# Редактирование товара
def edit_product(product_name: str,
                 category: str = None, price: int = None, description: str = None, img_link: str = None):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    if category is not None:
        cursor.execute('''UPDATE products SET category = ?  WHERE name = ?''', (category, product_name))
    if price is not None:
        cursor.execute('''UPDATE products SET price = ?  WHERE name = ?''', (price, product_name))
    if description is not None:
        cursor.execute('''UPDATE products SET description = ?  WHERE name = ?''', (description, product_name))
    if img_link is not None:
        cursor.execute('''UPDATE products SET img_link = ?  WHERE name = ?''', (img_link, product_name))
    conn.commit()


# Добавление ключей
def add_keys(product_name: str, keys: list):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    for i in keys:
        cursor.execute('''INSERT INTO ? (key) VALUES (?)''', (product_name, i))
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


# перенос ключей из таблицы активных в такблицу неактивных
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


def show_product(product_name):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM products WHERE name = ? LIMIT 1''', (product_name,))
    fetchall = cursor.fetchall()[0]
    price, description, img_link, in_stock = fetchall[2], fetchall[3], fetchall[4], fetchall[5]
    string = f'{product_name}\nЦена — {price}\nВ наличии: {in_stock}\n{description}'
    result = [string, img_link]
    return result


'''
пример обработки фото
@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(msg: types.Message):
    photo = msg.photo[0]['file_id']
    await bot.send_photo(msg.chat.id, photo)
    print(msg.caption)
'''


@dp.message_handler(commands=["get_state"], state='*')
async def cmd_catalog(msg: types.Message):
    state = await dp.current_state().get_state()
    await bot.send_message(msg.chat.id, str(state))


@dp.message_handler(commands=["catalog"], state='*')
async def cmd_catalog(msg: types.Message):
    markup = gen_catalog()
    button_filters = InlineKeyboardButton('фильтры', callback_data='filters')
    markup = markup.add(button_filters)
    await dp.current_state().set_state('catalog')
    await bot.send_message(msg.chat.id, 'Выберите товар', reply_markup=markup)


@dp.callback_query_handler(lambda callback: callback.data == 'to_admin_panel', state='*')
async def callback_admin(callback: types.callback_query):
    await dp.current_state().set_state('admin_panel')
    await bot.send_message(callback.from_user.id, messages.choose_action, reply_markup=markups.admin_panel)


@dp.callback_query_handler(lambda callback: callback.data != 'fuck', state='catalog')
async def callback_catalog(callback: types.callback_query):
    product_name = callback.data
    usr_id = callback.from_user.id
    if callback.data != 'filters':
        answer = show_product(product_name)
        img_link = answer[1]
        answer = answer[0]
        if img_link == '' or img_link is None:
            await bot.send_message(usr_id, answer)
        else:
            if '/' in img_link:
                with open(img_link, 'rb') as photo:  # чтобы отправить фото нужно открыть файл(причем бинарно), а не просто юзать путь к нему. хуй знает как я должен был это узнать, ебался 3 часа, пока не узнал, не помню уже где и как
                    await bot.send_photo(usr_id, photo=photo, caption=answer, reply_markup=markups.product)
                    await dp.current_state().set_state('product_watching')
            else:
                await bot.send_photo(usr_id, photo=img_link, caption=answer, reply_markup=markups.product)
                await dp.current_state().set_state('product_watching')
    else:
        await bot.send_message(usr_id, 'укажите фильтры', reply_markup=markups.catalog_filters)
        await dp.current_state().set_state('catalog_filters')


@dp.callback_query_handler(lambda callback: callback.data != 'fuck', state='product_watching')
async def callback_product(callback: types.callback_query):
    state = dp.current_state()
    usr_id = callback.from_user.id
    if callback.data == 'buy':
        # TODO: перейти на страницу оплаты
        await bot.send_message(usr_id, 'pay money, bitch')
    elif callback.data == 'to_cart':
        await bot.send_message(usr_id, 'Какая корзина тебе 13')
    elif callback.data == 'catalog':
        markup = gen_catalog()
        button_filters = InlineKeyboardButton('фильтры', callback_data='filters')
        markup = markup.add(button_filters)
        await state.set_state('catalog')
        await bot.send_message(usr_id, 'Выберите товар', reply_markup=markup)
    elif callback.data == 'filters':
        await state.set_state('choose_filter')
        await bot.send_message(usr_id, 'выберите фильтр', reply_markup=markups.catalog_filters)
        await dp.current_state().set_state('catalog_filters')


@dp.callback_query_handler(lambda callback: callback.data != 'fuck', state='add_description')
async def callback_description(callback: types.callback_query):
    state = dp.current_state()
    usr_id = callback.from_user.id
    if callback.data == 'new_product':
        await state.set_state('new_product')
        await bot.send_message(usr_id, messages.new_product, reply_markup=markups.to_admin_panel)
    elif callback.data == 'to_admin_panel':
        await state.set_state('admin_panel')
        await bot.send_message(usr_id, messages.choose_action, reply_markup=markups.admin_panel)


@dp.message_handler(commands=["start"], state='*')
async def cmd_start(msg: types.Message):
    usr_id = msg.chat.id
    await bot.send_message(usr_id, messages.start)
    state = dp.current_state(user=msg.from_user.id)
    new_user(usr_id)
    await state.reset_state()
    await state.set_state('enter_name')


@dp.message_handler(commands=["help"], state='*')
async def cmd_help(msg: types.Message):
    await bot.send_message(msg.chat.id, messages.help)

@dp.message_handler(commands=["admin"], state='*')
async def cmd_admin(msg: types.Message):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    usr_id = msg.chat.id
    state = dp.current_state(user=msg.from_user.id)
    cursor.execute('''SELECT * FROM users WHERE _id = ? LIMIT 1''', (usr_id,))
    is_admin = cursor.fetchall()[0][2]
    print(is_admin)
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
async def admin_panel(msg: types.Message):  # TODO: сделать админку
    usr_id = msg.chat.id
    state = dp.current_state(user=msg.from_user.id)
    if msg.text == 'Добавить товар':
        await state.set_state('new_product')
        await bot.send_message(usr_id, messages.new_product, reply_markup=markups.to_admin_panel)
    elif msg.text == 'Удалить товары':
        await state.set_state('delete_product')
        await bot.send_message(usr_id, messages.delete_product, reply_markup=markups.to_admin_panel)
    elif msg.text == 'Редактировать товар': # TODO редактировние товара
        await state.set_state('edit_product')
        await bot.send_message(usr_id, messages.edit_product, reply_markup=markups.to_admin_panel)
    elif msg.text == 'Добавить ключи к товару':
        await state.set_state('add_keys')
        await bot.send_message(usr_id, messages.add_keys, reply_markup=markups.to_admin_panel)
    elif msg.text == 'Удалить ключи товара':
        await state.set_state('delete_keys')
        await bot.send_message(usr_id, messages.delete_keys, reply_markup=markups.to_admin_panel)
    elif msg.text == 'Переместить ключи в проданные':
        await state.set_state('sell_keys')
        await bot.send_message(usr_id, messages.sell_keys, reply_markup=markups.to_admin_panel)


@dp.message_handler(content_types=['photo'], state='new_product')
async def product_creation(msg: types.Message):
    usr_id = msg.chat.id
    state = dp.current_state()
    print('fucked')
    name, category, price = msg.caption.split()[:3]
    description = ' '.join(msg.caption.split()[3:])
    price = int(price)
    img_link = msg.photo[0]['file_id']
    new_product(name, category=category, price=price, description=description, img_link=img_link)
    await bot.send_message(usr_id, f'Товар {name} успешно создан\n'
                                   f'Вы можете добавить ещё один товар, либо перейти в админ панель',
                           reply_markup=markups.to_admin_panel)


@dp.message_handler(state='new_product')
async def new_product_handler(msg: types.Message):
    usr_id = msg.chat.id
    state = dp.current_state()
    if msg.text == 'Перейти в админ-панель':
        await state.set_state('admin_panel')
        await bot.send_message(msg.chat.id, messages.choose_action, reply_markup=markups.admin_panel)
    else:
        await bot.send_message(usr_id, 'что-то пошло не так')


@dp.message_handler(state='delete_product')
async def delete_product_handler(msg: types.Message):
    usr_id = msg.chat.id
    state = dp.current_state()
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
            await bot.send_message(usr_id, f'товар {msg.text} удалён, вы можете продолжить либо перейти в админ панель', reply_markup=markups.to_admin_panel)
        except:
            await bot.send_message(usr_id, f'не удалось удалить товар {msg.text}', reply_markup=markups.to_admin_panel)


@dp.message_handler(state='enter_name')
async def enter_name(msg: types.Message):
    usr_id = msg.chat.id
    state = dp.current_state(user=msg.from_user.id)
    name = msg.text
    change_name(usr_id, name)
    await state.set_state('name_entered')
    await bot.send_message(usr_id, 'выберите действие', reply_markup=markups.catalog_or_filter)


@dp.message_handler(state='name_entered')
async def name_entered(msg: types.Message):
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
    usr_id = msg.chat.id
    state = dp.current_state()
    if msg.text == 'полный каталог':
        await cmd_catalog(msg)
        await state.set_state('catalog')
    elif msg.text == 'цена':
        await state.set_state('price_filter')
        await bot.send_message(usr_id, 'укажите нижнюю и верхнюю границы цены через пробел')
    elif msg.text == 'тип':
        # TODO: фильтр по типу(не срочно)
        pass
    elif msg.text == 'Поиск по названию':
        await state.set_state('search_product')
        await bot.send_message(usr_id, 'введите название')


@dp.message_handler(state='price_filter')
async def catalog_filters(msg: types.Message):
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
async def catalog_filters(msg: types.Message):
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
    print('wtf')

if __name__ == '__main__':
    executor.start_polling(dp)
