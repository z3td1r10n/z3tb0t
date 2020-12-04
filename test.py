import config
import sqlite3
from states import States
import markups





def show_catalog(price=None, category=None, product_name=None, page_lenght = 10):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    if product_name is not None:
        cursor.execute('''SELECT * FROM products WHERE name LIKE '%{}%' LIMIT 1'''.format(product_name))
    elif price is not None and category is not None:
        cursor.execute('''SELECT * FROM products WHERE price <= ? AND category = ?''', (price, category))
    elif price is not None:
        cursor.execute('''SELECT * FROM products WHERE price <= ?''', (price,))
    elif category is not None:
        cursor.execute('''SELECT * FROM products WHERE category = ?''', (category,))
    else:
        cursor.execute('''SELECT * FROM products''')

    markup = InlineKeyboardMarkup()
    pages = []
    c = 1
    for product in cursor.fetchall():
        if c <= page_lenght:
            button = InlineKeyboardButton(product[0] + ' ' + str(product[2]))
            markup.add(button)
        else:
            pages.append(markup)
            markup = InlineKeyboardMarkup()
            c = 1
            button = InlineKeyboardButton(product[0] + ' ' + str(product[2]))
            markup.add(button)
    if pages == []:
        pages.append(markup)
    print(pages)
    return pages


