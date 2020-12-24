import sqlite3

db_name = '../data/database.db'
connection = sqlite3.connect(dbname)

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (dname, spotify_url, image_url) VALUES (?, ?, ?)",
            ('Bin Xuan Kong', 'https://open.spotify.com/user/12120382831', 'https://scontent-hkt1-2.xx.fbcdn.net/v/t1.0-1/p320x320/11988649_10205375733654944_669349554023656758_n.jpg?_nc_cat=110&ccb=2&_nc_sid=0c64ff&_nc_ohc=qNH7qntD3ukAX-nqGgf&_nc_ht=scontent-hkt1-2.xx&tp=6&oh=412236df77fa5d56b351efeffe5f7f89&oe=6009A752')
           )

connection.commit()
connection.close()