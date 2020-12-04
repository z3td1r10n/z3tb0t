import sqlite3

# подключение к БД, далее не комментируется
conn = sqlite3.connect("data.db")
cursor = conn.cursor()
# -----

cursor.execute('''SELECT * FROM products''')
print(cursor.fetchall())