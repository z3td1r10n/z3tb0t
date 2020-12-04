import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()


try:
    cursor.execute('''DROP TABLE products''')
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


with open('data.txt', 'r', encoding='UTF-8') as file:
    for line in file:
        if '\n' in line:
            line.replace('\n', '')
        print(line)
        name, category, price, img_link, in_stock, description = line.split()
        price = int(price)
        in_stock = int(in_stock)
        print(price)
        print(in_stock)
        cursor.execute('''INSERT INTO products (name, category, price, img_link, in_stock, description) 
        VALUES (?, ?, ?, ?, ?, ?)''', (name, category, price, img_link, in_stock, description))


conn.commit()
