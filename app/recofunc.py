import os
import pandas as pd
import spotipy
import datetime as dt
from sqlalchemy import create_engine
from spotipy.oauth2 import SpotifyClientCredentials
from app.queries import recommend_artists_query, recommend_tracks_query, top_artists3_query, top_tracks3_query
from app.dbfunc import sync_data, update_artists_and_tracks

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_recommendations(user_id):
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_query('SELECT last_recommended FROM "Users" WHERE user_id=%(user_id)s', engine, params={'user_id': user_id})
    if not isinstance(df['last_recommended'].min(), dt.datetime):
        df_ra, df_rt = get_new_recommendations(user_id)
    elif (dt.datetime.now() - df['last_recommended'].min()).days >= 1:
        df_ra, df_rt = get_new_recommendations(user_id)
    else:
        engine = create_engine(DATABASE_URL)
        df_ra = pd.read_sql_query(recommend_artists_query, engine, params={'user_id': user_id})
        df_rt = pd.read_sql_query(recommend_tracks_query, engine, params={'user_id': user_id})
    return df_ra, df_rt

def get_new_recommendations(user_id):
    engine = create_engine(DATABASE_URL)
    # Get user's top artists and tracks
    df_a = pd.read_sql_query(top_artists3_query, engine, params={'user_id': user_id})
    df_t = pd.read_sql_query(top_tracks3_query, engine, params={'user_id': user_id})
    # Get recommendations
    df_ra = recommend_artists(df_a)
    df_rt = recommend_tracks(df_t)
    # Sync user data
    engine.execute('UPDATE "Users" SET last_recommended = %(last_recommended)s WHERE user_id = %(user_id)s', \
        last_recommended=dt.datetime.now(), user_id=user_id)
    sync_data(df_ra[['user_id', 'artist_id']], 'RecommendArtists', engine)
    sync_data(df_rt[['user_id', 'track_id']], 'RecommendTracks', engine)
    # Sync artists and tracks
    df_ra.drop(columns=['user_id']).to_sql('TempArtists', engine, index=False, if_exists='replace')
    df_rt.drop(columns=['user_id']).to_sql('TempTracks', engine, index=False, if_exists='replace')
    update_artists_and_tracks(engine)
    # Dispose engine
    engine.dispose()
    return df_ra, df_rt

def recommend_artists(df):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    user_id = df['user_id'].unique()[0]
    recom_list = []
    seed_artists = df['artist_id'].iloc[:5].tolist()
    for seed in seed_artists:
        recom = sp.artist_related_artists(seed)
        for a in recom['artists']:
            if a['id'] not in df['artist_id'].iloc[:20]:
                this_recom = {
                    'user_id': user_id,
                    'artist_id': a['id'],
                    'artist': a['name'],
                    'genres': "; ".join(g for g in a['genres']),
                    'artist_url': a['external_urls']['spotify'],
                    'artist_image': a['images'][0]['url'],
                    'popularity': a['popularity']
                }
                recom_list.append(this_recom)
    if len(recom_list) >= 20:
        return pd.DataFrame.from_dict(recom_list).sample(n=20)
    else:
        return pd.DataFrame.from_dict(recom_list)

def recommend_tracks(df):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    user_id = df['user_id'].unique()[0]
    seed_tracks = df['track_id'].iloc[:5].tolist()
    recom = sp.recommendations(seed_tracks=seed_tracks, limit=50)
    recom_list = []
    for t in recom['tracks']:
        if t['id'] not in df['track_id'].iloc[:20]:
            this_recom = {
                'user_id': user_id,
                'track_id': t['id'],
                'track_id': t['id'],
                'track': t['name'],
                'artists': "; ".join(a['name'] for a in t['artists']),
                'album': t['album']['name'],
                'album_image': t['album']['images'][0]['url'],
                'release_date': t['album']['release_date'],
                'track_url': t['external_urls']['spotify']
            }
            recom_list.append(this_recom)
        if len(recom_list) >= 30:
            break
    return pd.DataFrame.from_dict(recom_list)