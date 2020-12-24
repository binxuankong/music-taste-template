import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyOAuth

secrets = {
    "Client Id": "e08da5aa4af243e2ac533ca96170a077",
    "Client Secret": "116b8f9c375d467c9a1722af618923eb"
}

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