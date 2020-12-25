import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyOAuth

secrets = {
    "Client Id": "e08da5aa4af243e2ac533ca96170a077",
    "Client Secret": "116b8f9c375d467c9a1722af618923eb"
}

RANGES = {'short_term': 'Short term', 'medium_term': 'Medium term', 'long_term': 'Long term'}
LIMIT = 20

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

def get_spotify_connection():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=secrets["Client Id"],
                                                   client_secret=secrets["Client Secret"],
                                                   redirect_uri="https://music-taste-d.herokuapp.com/callback",
                                                   scope="user-top-read"))
    return sp

def get_user_profile(sp):
    results = sp.me()
    user_profile = {'display_name': results['display_name'],
                    'spotify_url': results['external_urls']['spotify'],
                    'image_url': results['images'][0]['url']}
    return user_profile

def get_top_artists(sp, time_frame='long_term', limit=LIMIT):
    results = sp.current_user_top_artists(time_range=time_frame, limit=limit)
    top_artists = []
    for i, item in enumerate(results['items']):
        top_artists.append({'Rank': i+1,
                            'Artist': item['name'],
                            'Genres': item['genres'],
                            'Timeframe': RANGES[time_frame]})
    return top_artists

def get_top_tracks(sp, time_frame='long_term', limit=LIMIT):
    results = sp.current_user_top_tracks(time_range=time_frame, limit=limit)
    top_tracks = []
    for i, item in enumerate(results['items']):
        track = item['name']
        artist = item['artists'][0]['name']
        album = item['album']['name']
        duration = int(item['duration_ms'])
        minute = int((duration / (1000*60)) % 60)
        second = int((duration / 1000) % 60)
        duration = str(minute) + ':' + str(second)
        top_tracks.append({'Rank': i+1,
                           'Track': track,
                           'Artist': artist,
                           'Album': album,
                           'Duration': duration,
                           'Timeframe': RANGES[time_frame]})
    return top_tracks