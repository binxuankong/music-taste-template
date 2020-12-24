import os
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from app.functions import get_db_connection, get_user, get_spotify_connection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CALIWASAMISSIONBUTNOWAGLEAVING'

@app.route('/')
def index():
    con = get_db_connection()
    users = con.execute('SELECT * FROM users').fetchall()
    con.close()
    return render_template('index.html', users=users)

@app.route('/<int:user_id>')
def user(user_id):
    user = get_user(user_id)
    return render_template('user.html', user=user)

@app.route('/link', methods=('GET', 'POST'))
def link():
    if request.method == 'POST':
        sp = get_spotify_connection()
        user_info = sp.me()
    
        if not user_info:
            flash("Unable to access to user!")
        else:
            dname = user_info['display_name']
            spotify_url = user_info['external_urls']['spotify']
            image_url = user_info['images']['url']
            con = get_db_connection()
            con.execute("""INSERT INTO users (dname, spotify_url, image_url) VALUES (?, ?, ?)
                        SELECT *
                        WHERE NOT EXISTS (SELECT 1 FROM users WHERE spotify_url = '{}')
                        """.format(spotify_url),
                        (dname, spotify_url, image_url))
            con.commit()
            con.close()
            return redirect(url_for('index'))

    return render_template('link.html')