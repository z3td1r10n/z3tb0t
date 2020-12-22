from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


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
    resize_keyboard=True, row_width=2
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


button_create_product = KeyboardButton('Добавить товар')
button_delete_product = KeyboardButton('Удалить товары')
button_to_admin_panel = InlineKeyboardButton('Перейти в админ-панель', callback_data='to_admin_panel')
button_new_product = InlineKeyboardButton('Новый товар', callback_data='new_product')
button_inline_catalog = InlineKeyboardButton('полный каталог', callback_data='catalog')

to_catalog = InlineKeyboardMarkup().add(button_inline_catalog)

admin_panel = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).row(button_create_product, button_delete_product)

to_admin_panel = InlineKeyboardMarkup(
    resize_keyboard=True
).add(button_to_admin_panel)
