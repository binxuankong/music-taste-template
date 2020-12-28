import os
import json
import requests
import spotipy
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from app.spotifunc import get_user_df
from app.dbfunc import update_user_profile, get_top_artists, get_top_tracks

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CALIWASAMISSIONBUTNOWAGLEAVING'

API_BASE = "https://accounts.spotify.com"
SCOPE = "user-read-recently-played user-top-read"
REDIRECT_URI = os.environ.get('SPOTIFY_CALLBACK_URI')
CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

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

@app.route("/view_credentials", methods = ["POST", "GET"])
def view_credentials():

    if request.method == "GET":
        if request.form.get('submit_button') == 'View Admin':
            output = db.execute('SELECT * FROM admin').fetchall()
            return render_template("adminDashboard.html", output=output)
        elif request.form.get('submit_button') == 'View Tutor':
            output = db.execute('SELECT * FROM login_signup_tutor').fetchall()
            return render_template("adminDashboard.html", output=output)

@app.route('/profile', methods = ["POST", "GET"])
def profile():
    if 'token' in session:
        sp = spotipy.Spotify(auth=session['token'])
        # Get user profile
        df_user = get_user_df(sp)
        user_profile = update_user_profile(df_user)
        timeframe = ('short_term', 'Recent')
        if request.method == "POST":
            if request.form.get('range_button') == 'All time':
                timeframe = ('long_term', 'All time')
            elif request.form.get('range_button') == 'Past few months':
                timeframe = ('medium_term', 'Past few months')
            elif request.form.get('range_button') == 'Recent':
                timeframe = ('short_term', 'Recent')
        top_artists = get_top_artists(sp, timeframe[0])
        top_tracks = get_top_tracks(sp, timeframe[0])
        return render_template('profile.html', user=user_profile, artists=top_artists, tracks=top_tracks, session=session, timeframe=timeframe[1])
    return render_template('profile.html', user=None)