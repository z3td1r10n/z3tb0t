import sqlite3
import main

# подключение к БД, далее не комментируется
conn = sqlite3.connect("data.db")
cursor = conn.cursor()
# -----



cursor.execute('''SELECT * FROM users WHERE _id = ?''', (123,))

print(main.make_dict(cursor.fetchall()[0][-1]))

