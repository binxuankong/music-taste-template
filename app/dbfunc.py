import os
import pandas as pd
from sqlalchemy import create_engine
from app.queries import user_update_query, user_query, top_artists_query, top_tracks_query, top_genres_query, music_features_query
from app.spotifunc import get_user_df, get_recently_played_df, get_current_playlists_df, get_top_artists_df, get_top_tracks_df, \
                          get_top_genres_df

TABLES = ['Users', 'RecentlyPlayed', 'CurrentPlaylists', 'TopArtists', 'TopTracks']
DATABASE_URL = os.environ.get('DATABASE_URL')

def update_user_profile(df_user):
    engine = create_engine(DATABASE_URL)
    u = df_user.to_dict('records')[0]
    df_exist = pd.read_sql_query('SELECT * FROM "Users" u WHERE u.user_id = %(user_id)s', engine, \
                                 params={'user_id': u['user_id']})
    if len(df_exist) == 0:
        df_user.to_sql('Users', engine, if_exists='append', index=False)
    else:
        engine.execute(user_update_query, user_id=u['user_id'], display_name=u['display_name'], spotify_url=u['spotify_url'], \
            image_url=u['image_url'], followers=u['followers'], last_login=u['last_login'])
    engine.dispose()
    return u

def get_user_profile(user_id):
    engine = create_engine(DATABASE_URL)
    df_user = pd.read_sql_query(user_query, engine, params={'user_id': user_id})
    user_profile = df_user.to_dict('records')[0]
    engine.dispose()
    return user_profile

def get_top_artists(user_id):
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_query(top_artists_query, engine, params={'user_id': user_id})
    engine.dispose()
    return top_to_dict(df)

def get_top_tracks(user_id):
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_query(top_tracks_query, engine, params={'user_id': user_id})
    engine.dispose()
    return top_to_dict(df)

def get_top_genres(user_id):
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_query(top_genres_query, engine, params={'user_id': user_id})
    engine.dispose()
    return df

def get_music_features(user_id):
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_query(music_features_query, engine, params={'user_id': user_id})
    engine.dispose()
    return top_to_dict(df)

def sync_all_data(sp):
    engine = create_engine(DATABASE_URL)
    # User profile
    df_user = get_user_df(sp)
    sync_data(df_user, 'Users', engine)
    # Recently played
    #df_rp = get_recently_played_df(sp)
    #sync_data(df_rp, 'RecentlyPlayed', engine)
    # Current playlists
    #df_cp = get_current_playlists_df(sp)
    #sync_data(df_cp, 'CurrentPlaylists', engine)
    # Top artists
    df_ta = get_top_artists_df(sp)
    sync_data(df_ta, 'TopArtists', engine)
    # Top tracks
    df_tt = get_top_tracks_df(sp)
    sync_data(df_tt, 'TopTracks', engine)
    # Dispose engine
    engine.dispose()
    #return df_user, df_rp, df_cp, df_ta, df_tt
    return df_user, df_ta, df_tt

def sync_data(df, table, engine):
    if len(df) > 0:
        delete_user_data(df, table, engine)
        insert_new_data(df, table, engine)

def delete_user_data(df, table, engine):
    user_id = df['user_id'][0]
    # timeframe = df['timeframe'][0]
    # engine.execute('DELETE FROM "{}" WHERE user_id = %(user_id)s AND timeframe = %(timeframe)s'.format(table), user_id=user_id, timeframe=timeframe)
    engine.execute('DELETE FROM "{}" WHERE user_id = %(user_id)s'.format(table), user_id=user_id)

def insert_new_data(df, table, engine):
    df.to_sql(table, engine, index=False, if_exists='append')

def top_to_dict(top_df):
    top_dict = {}
    top_dict['Short'] = top_df.loc[top_df['timeframe'] == 'Short'].to_dict('records')
    top_dict['Medium'] = top_df.loc[top_df['timeframe'] == 'Medium'].to_dict('records')
    top_dict['Long'] = top_df.loc[top_df['timeframe'] == 'Long'].to_dict('records')
    return top_dict