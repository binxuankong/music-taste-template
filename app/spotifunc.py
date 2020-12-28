import pandas as pd
import datetime as dt
import spotipy
from spotipy.oauth2 import SpotifyOAuth

RANGES = {'short_term': 'Short', 'medium_term': 'Medium', 'long_term': 'Long'}
LIMIT = 50

def get_user_df(sp):
    user = sp.me()
    df_user = pd.DataFrame({
        'user_id': user['id'],
        'display_name': user['display_name'],
        'spotify_url': user['external_urls']['spotify'],
        'image_url': user['images'][0]['url'],
        'followers': user['followers']['total'],
        'date_created': dt.datetime.now(),
        'last_login': dt.datetime.now()
    }, index=[0])
    return df_user

def get_recently_played_df(sp):
    user_id = sp.me()['id']
    recently_played = sp.current_user_recently_played()
    dict_list = []
    for rp in recently_played['items']:
        this_track = {
            'user_id': user_id,
            'track': rp['track']['name'],
            'artists': "; ".join(a['name'] for a in rp['track']['artists']),
            'album': rp['track']['album']['name'],
            'release_date': rp['track']['album']['release_date'],
            'track_url': rp['track']['external_urls']['spotify'],
            'played_at': rp['played_at']
        }
        dict_list.append(this_track)
    return pd.DataFrame.from_dict(dict_list)

def get_current_playlists_df(sp):
    user_id = sp.me()['id']
    user_playlists = sp.current_user_playlists()
    dict_list = []
    for pl in user_playlists['items']:
        this_playlist = {
            'user_id': user_id,
            'playlist_id': pl['id'],
            'name': pl['name'],
            'description': pl['description'],
            'owner_display_name': pl['owner']['display_name'],
            'playlist_url': pl['external_urls']['spotify'],
            'track_numbers': pl['tracks']['total']
        }
        dict_list.append(this_playlist)
    return pd.DataFrame.from_dict(dict_list)

def get_top_artists_df(sp, timeframe):
    user_id = sp.me()['id']
    top_list = []
    top_artists = sp.current_user_top_artists(time_range=timeframe, limit=LIMIT)
    for i, a in enumerate(top_artists['items']):
        this_artist = {
            'user_id': user_id,
            'rank': i+1,
            'artist': a['name'],
            'genres': "; ".join(g for g in a['genres']),
            'artist_url': a['external_urls']['spotify'],
            'timeframe': RANGES[timeframe]
        }
        top_list.append(this_artist)
    return pd.DataFrame.from_dict(top_list)

def get_top_tracks_df(sp, timeframe):
    user_id = sp.me()['id']
    top_list = []
    top_tracks = sp.current_user_top_tracks(time_range=timeframe, limit=LIMIT)
    for i, t in enumerate(top_tracks['items']):
        this_track = {
            'user_id': user_id,
            'rank': i+1,
            'track': t['name'],
            'artists': "; ".join(a['name'] for a in t['artists']),
            'album': t['album']['name'],
            'release_date': t['album']['release_date'],
            'track_url': t['external_urls']['spotify'],
            'timeframe': RANGES[timeframe]
        }
        top_list.append(this_track)
    return pd.DataFrame.from_dict(top_list)