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