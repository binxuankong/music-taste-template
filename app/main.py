import os
import json
import requests
import spotipy
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from app.functions import get_db_connection, get_user, get_spotify_connection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CALIWASAMISSIONBUTNOWAGLEAVING'

API_BASE = "https://accounts.spotify.com"
# REDIRECT_URI = "http://music-taste-d.herokuapp.com/callback"
REDIRECT_URI = "http://127.0.0.1:5000/callback"
SCOPE = "user-read-recently-played user-top-read"
CLIENT_ID = "e08da5aa4af243e2ac533ca96170a077"
CLIENT_SECRET = "116b8f9c375d467c9a1722af618923eb"

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

@app.route('/verify')
def verify():
    auth_url = f"{API_BASE}/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    auth_token_url = f"{API_BASE}/api/token"
    res = requests.post(auth_token_url, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    res_body = res.json()
    session['token'] = res_body.get('access_token')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'token' in session:
        sp = spotipy.Spotify(auth=session['token'])
        user_profile = sp.me()
        user = {'display_name': user_profile['display_name'],
                'spotify_url': user_profile['external_urls']['spotify'],
                'image_url': user_profile['images'][0]['url']}
        return render_template('profile.html', user=user)

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