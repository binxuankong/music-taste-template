import sqlite3

def get_db_connection():
    db_name = 'data/database.db'
    con = sqlite3.connect(db_name)
    con.row_factory = sqlite3.Row
    return con

def get_user(user_id):
    con = get_db_connection()
    user = con.execute('SELECT * FROM users WHERE id = ?',
                       (user_id,)).fetchone()
    con.close()
    if user is None:
        abort(404)
    return user