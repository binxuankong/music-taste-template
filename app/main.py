import os
import json
import requests
import spotipy
import pandas as pd
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from app.spotifunc import get_user_df
from app.dbfunc import get_user_profile, get_top_artists, get_top_tracks, get_top_genres, get_music_features, create_new_user, \
    sync_all_data, update_user_privacy, update_user_code
from app.vizfunc import plot_genre_chart, plot_mood_gauge

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
        try:
            # Authenticate Spotify session
            sp = spotipy.Spotify(auth=session['token'])
            df_user = get_user_df(sp)
            user_id = df_user['user_id'][0]
            session['user_id'] = user_id
            # Get data from database
            user_profile = get_user_profile(user_id)
            if user_profile is None:
                return redirect(url_for('new'))
            top_artists = get_top_artists(user_id)
            top_tracks = get_top_tracks(user_id)
            top_genres = get_top_genres(user_id)
            music_features = get_music_features(user_id)
            # Plot charts
            genre_data = plot_genre_chart(top_genres)
            mood_data = plot_mood_gauge(music_features)
            return render_template('profile.html', user=user_profile, artists=top_artists, tracks=top_tracks, genres=genre_data, moods=mood_data)
        except:
            return render_template('profile.html', user=None)
    return render_template('profile.html', user=None)

@app.route('/new')
def new():
    if 'token' in session:
        # Authenticate Spotify session
        sp = spotipy.Spotify(auth=session['token'])
        success = create_new_user(sp)
        if success:
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('index'))
    return redirect(url_for('link'))

@app.route('/update')
def update():
    if 'token' in session:
        # Authenticate Spotify session
        sp = spotipy.Spotify(auth=session['token'])
        success = sync_all_data(sp)
        if success:
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('index'))
    return redirect(url_for('link'))

@app.route('/privacy')
def privacy():
    if 'user_id' in session:
        success = update_user_privacy(session['user_id'])
        if success:
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('index'))
    return redirect(url_for('link'))

@app.route('/code')
def code():
    if 'user_id' in session:
        success = update_user_code(session['user_id'])
        if success:
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('index'))
    return redirect(url_for('link'))