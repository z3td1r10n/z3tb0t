import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()


try:
    cursor.execute('''DROP TABLE products''')
    cursor.execute('''DROP TABLE users''')
except:
    pass


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


cursor.execute('''CREATE TABLE users
(
    _id INTEGER PRIMARY KEY,
    name TEXT,
    is_admin INTEGER,
    basket TEXT,
    temp TEXT
)
''')
