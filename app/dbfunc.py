import os
import random
import pandas as pd
from sqlalchemy import create_engine
from app.codes import NOUNS, ADJECTIVES
from app.queries import user_query, top_artists_query, top_tracks_query, top_genres_query, music_features_query, user_update_query, \
    user_privacy_query, user_code_query, artists_update_query, tracks_update_query
from app.spotifunc import get_user_df, get_top_artists_df, get_top_tracks_df, get_top_genres_df, get_music_features_df

TABLES = ['Users', 'RecentlyPlayed', 'CurrentPlaylists', 'TopArtists', 'TopTracks']
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_user_profile(user_id):
    try:
        engine = create_engine(DATABASE_URL)
        df_user = pd.read_sql_query(user_query, engine, params={'user_id': user_id})
        user_profile = df_user.to_dict('records')[0]
        engine.dispose()
        return user_profile
    except:
        return None

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

def create_new_user(sp):
    try:
        df_user = get_user_df(sp)
        user_id = df_user['user_id'][0]
        success = sync_all_data(sp)
        # Create user profile
        engine = create_engine(DATABASE_URL)
        df_codes = pd.read_sql_query('SELECT code FROM "UserProfiles"', engine)
        existing_codes = df_codes['code'].unique().tolist()
        while True:
            code = random.choice(ADJECTIVES) + '-' + random.choice(NOUNS) + '-' + str(random.randint(10, 99))
            if code not in existing_codes:
                break
        df_profile = pd.DataFrame([[user_id, code, False]], columns=['user_id', 'code', 'public'])
        df_profile.to_sql('UserProfiles', engine, index=False, if_exists='append')
        # Dispose engine
        engine.dispose()
        return True
    except:
        return False

def sync_all_data(sp):
    try:
        engine = create_engine(DATABASE_URL)
        # Extract from Spotify API
        df_user = get_user_df(sp)
        df_ta = get_top_artists_df(sp)
        df_tt = get_top_tracks_df(sp)
        df_tg = get_top_genres_df(top_to_dict(df_ta))
        df_mf = get_music_features_df(sp, top_to_dict(df_tt))
        # Artists and tracks
        df_a = df_ta.drop(columns=['user_id', 'rank', 'timeframe']).drop_duplicates()
        df_t = df_tt.drop(columns=['user_id', 'rank', 'timeframe']).drop_duplicates()
        # Sync user data
        user_profile = update_user_profile(df_user)
        sync_data(df_ta[['user_id', 'rank', 'artist_id', 'timeframe']], 'TopArtists', engine)
        sync_data(df_tt[['user_id', 'rank', 'track_id', 'timeframe']], 'TopTracks', engine)
        sync_data(df_tg, 'TopGenres', engine)
        sync_data(df_mf, 'MusicFeatures', engine)
        # Sync artists and tracks
        df_a.to_sql('TempArtists', engine, index=False, if_exists='replace')
        df_t.to_sql('TempTracks', engine, index=False, if_exists='replace')
        engine.execute(artists_update_query)
        engine.execute(tracks_update_query)
        # Dispose engine
        engine.dispose()
        return True
    except:
        return False

def update_user_profile(df_user):
    engine = create_engine(DATABASE_URL)
    u = df_user.to_dict('records')[0]
    df_exist = pd.read_sql_query('SELECT * FROM "Users" u WHERE u.user_id = %(user_id)s', engine, \
                                 params={'user_id': u['user_id']})
    if len(df_exist) == 0:
        df_user.to_sql('Users', engine, if_exists='append', index=False)
    else:
        engine.execute(user_update_query, user_id=u['user_id'], display_name=u['display_name'], spotify_url=u['spotify_url'], \
            image_url=u['image_url'], followers=u['followers'], last_updated=u['last_updated'])
    engine.dispose()
    return u

def update_user_privacy(user_id):
    try:
        engine = create_engine(DATABASE_URL)
        engine.execute(user_privacy_query, user_id=user_id)
        engine.dispose()
        return True
    except:
        return False

def update_user_code(user_id):
    try:
        engine = create_engine(DATABASE_URL)
        df_codes = pd.read_sql_query('SELECT code FROM "UserProfiles"', engine)
        existing_codes = df_codes['code'].unique().tolist()
        while True:
            code = random.choice(ADJECTIVES) + '-' + random.choice(NOUNS) + '-' + str(random.randint(10, 99))
            if code not in existing_codes:
                break
        engine.execute(user_code_query, user_id=user_id, code=code)
        engine.dispose()
        return True
    except:
        return False

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