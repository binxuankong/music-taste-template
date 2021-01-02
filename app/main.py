import os
import json
import requests
import spotipy
import pandas as pd
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from app.spotifunc import get_user_df
from app.dbfunc import update_user_profile, get_top_artists, get_top_tracks, get_top_genres

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
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    if 'token' in session:
        sp = spotipy.Spotify(auth=session['token'])
        # Get user profile
        df_user = get_user_df(sp)
        user_profile = update_user_profile(df_user)
        top_artists = get_top_artists(sp)
        top_tracks = get_top_tracks(sp)
        top_genres = get_top_genres(top_artists)
        return render_template('profile.html', user=user_profile, artists=top_artists, tracks=top_tracks, genres=top_genres)
    return render_template('profile.html', user=None)

@app.route('/sample')
def sample():
    def top_to_dict(top_df):
        top_dict = {}
        top_dict['Short'] = top_df.loc[top_df['timeframe'] == 'Short'].to_dict('records')[:10]
        top_dict['Medium'] = top_df.loc[top_df['timeframe'] == 'Medium'].to_dict('records')[:10]
        top_dict['Long'] = top_df.loc[top_df['timeframe'] == 'Long'].to_dict('records')[:10]
        return top_dict
    user_profile = {'user_id': '12120382831',
    'display_name': 'Bin Xuan Kong',
    'spotify_url': 'https://open.spotify.com/user/12120382831',
    'image_url': 'https://scontent-hkt1-2.xx.fbcdn.net/v/t1.0-1/p320x320/11988649_10205375733654944_669349554023656758_n.jpg?_nc_cat=110&ccb=2&_nc_sid=0c64ff&_nc_ohc=AJow9AVGs5YAX8M8_c_&_nc_ht=scontent-hkt1-2.xx&tp=6&oh=7e0addad9882e303c4df5928dd93401f&oe=600D9BD2',
    'followers': 53,
    'date_created': '2020-12-27 18:24:31.543185',
    'last_login': '2020-12-27 18:24:31.543192'}
    top_artists = pd.read_csv('data/top_artists.csv')
    top_tracks = pd.read_csv('data/top_tracks.csv')
    top_genres = pd.read_csv('data/top_genres.csv')
    user_id = int(user_profile['user_id'])
    top_genres = get_top_genres(top_artists)
    top_artists = top_to_dict(top_artists.loc[top_artists['user_id'] == user_id])
    top_tracks = top_to_dict(top_tracks.loc[top_tracks['user_id'] == user_id])
    top_genres = top_to_dict(top_genres.loc[top_tracks['user_id'] == user_id])
    return render_template('profile.html', user=user_profile, artists=top_artists, tracks=top_tracks, genres=top_genres)