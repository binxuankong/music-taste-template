import os
import json
import requests
import spotipy
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from app.functions import get_db_connection, get_user, get_spotify_connection, get_user_profile, get_top_artists, get_top_tracks

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CALIWASAMISSIONBUTNOWAGLEAVING'

API_BASE = "https://accounts.spotify.com"
REDIRECT_URI = "http://music-taste-d.herokuapp.com/callback"
# REDIRECT_URI = "http://127.0.0.1:5000/callback"
SCOPE = "user-read-recently-played user-top-read"
CLIENT_ID = "e08da5aa4af243e2ac533ca96170a077"
CLIENT_SECRET = "116b8f9c375d467c9a1722af618923eb"

@app.route('/')
def index():
    if 'token' in session:
        return render_template('index.html', session=session)
    return render_template('index.html')

@app.route('/<int:user_id>')
def user(user_id):
    user = get_user(user_id)
    return render_template('user.html', user=user)

@app.route('/link')
def link():
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
        user_profile = get_user_profile(sp)
        top_artists = get_top_artists(sp)
        top_tracks = get_top_tracks(sp)
        return render_template('profile.html', user=user_profile, artists=top_artists, tracks=top_tracks, session=session)
    return render_template('profile.html')