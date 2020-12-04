from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


button_all_catalog = KeyboardButton('полный каталог')
button_go_to_filters = KeyboardButton('Фильтры')
button_filter_price = KeyboardButton('цена')
button_filter_category = KeyboardButton('тип')
button_search_product = KeyboardButton('Поиск по названию')
button_back_to_filters = KeyboardButton('Вернуться к фильтрам')
button_category1 = KeyboardButton('Тип 1')
button_category2 = KeyboardButton('Тип 2')
button_category3 = KeyboardButton('Тип 3')


catalog_or_filter = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True, row_width=2
).row(button_all_catalog, button_go_to_filters)


catalog_filters = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_all_catalog).add(button_filter_price).add(button_filter_category).add(button_search_product)


back_to_filters = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_back_to_filters)

categories = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_category1).add(button_category2).add(button_category3).add(button_back_to_filters)

# далее клавиатуры, связанные с админ панелью

button_create_product = KeyboardButton('Добавить товар')
button_delete_product = KeyboardButton('Удалить товары')
button_edit_product = KeyboardButton('Редактировать товар')
button_add_keys = KeyboardButton('Добавить ключи к товару')
button_delete_keys = KeyboardButton('Удалить ключи товара')
button_sell_keys = KeyboardButton('Переместить ключи в проданные')
button_to_admin_panel = InlineKeyboardButton('Перейти в админ-панель', callback_data='to_admin_panel')
button_new_product = InlineKeyboardButton('Новый товар', callback_data='new_product')


admin_panel = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(button_create_product).add(button_delete_product).add(button_edit_product)\
    .add(button_add_keys).add(button_delete_keys).add(button_sell_keys)

to_admin_panel = InlineKeyboardMarkup(
    resize_keyboard=True
).add(button_to_admin_panel)


button_to_cart = InlineKeyboardButton('В корзину', callback_data='to_cart')
button_buy = InlineKeyboardButton('Купить', callback_data='buy')
button_inline_catalog = InlineKeyboardButton('Каталог', callback_data='catalog')
product = InlineKeyboardMarkup(
    row_width=2, resize_keyboard=True, one_time_keyboard=True
).row(button_to_cart, button_buy).add(button_inline_catalog)
