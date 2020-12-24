import os
import sqlite3

def get_db_connection():
    db_name = os.path.dirname(os.path.abspath('../data')) + '/data/database.db'
    con = sqlite3.connect(db_name)
    con.row_factory = sqlite3.Row
    return con


cursor = get_db_connection()
users = cursor.execute('SELECT * FROM users').fetchall()
cursor.close()

print(users)