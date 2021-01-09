import os
import pandas as pd
from sqlalchemy import create_engine
from app.codes import ADJECTIVES, NOUNS
from app.queries import users2_query, top_artists2_query, top_tracks2_query, top_genres2_query, music_features2_query, \
    similar_artists_query, similar_tracks_query

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_user_from_code(code):
    try:
        code_parts = code.split('-')
        if len(code_parts) != 3 or code_parts[0] not in ADJECTIVES or code_parts[1] not in NOUNS or not (0 < int(code_parts[2]) < 100):
            return None
        engine = create_engine(DATABASE_URL)
        df_u = pd.read_sql('SELECT user_id FROM "UserProfiles" WHERE code = %(code)s', engine, params={'code': code})
        if len(df_u) != 1:
            return None
        return df_u['user_id'].item()
    except:
        return None

def compare_users(u1, u2):
    # Configs
    tf_weights = {'Short': 6, 'Medium': 5, 'Long': 4}
    mu_weights = {'artist': 4, 'track': 1, 'genre': 8, 'feature': 2}
    # Get data
    engine = create_engine(DATABASE_URL)
    users = pd.read_sql(users2_query, engine, params={'user_ids': (u1, u2)})
    df_a = pd.read_sql(top_artists2_query, engine, params={'user_ids': (u1, u2)})
    df_t = pd.read_sql(top_tracks2_query, engine, params={'user_ids': (u1, u2)})
    df_g = pd.read_sql(top_genres2_query, engine, params={'user_ids': (u1, u2)})
    df_m = pd.read_sql(music_features2_query, engine, params={'user_ids': (u1, u2)})
    # User 1
    u1_a = df_a.loc[df_a['user_id'] == u1]
    u1_t = df_t.loc[df_t['user_id'] == u1]
    u1_g = df_g.loc[df_g['user_id'] == u1]
    u1_m = df_m.loc[df_m['user_id'] == u1]
    # User 2
    u2_a = df_a.loc[df_a['user_id'] == u2]
    u2_t = df_t.loc[df_t['user_id'] == u2]
    u2_g = df_g.loc[df_g['user_id'] == u2]
    u2_m = df_m.loc[df_m['user_id'] == u2]
    
    final_points = 0
    similar_artists = pd.DataFrame()
    similar_tracks = pd.DataFrame()
    similar_genres = pd.DataFrame()
    
    name1 = users.loc[users['user_id'] == u1]['display_name'].unique().item()
    name2 = users.loc[users['user_id'] == u2]['display_name'].unique().item()
    print('Comparing {} and {}...'.format(name1, name2))

    for timeframe in ['Short', 'Medium', 'Long']:
        tf_points = 0
        # Artist
        df_artist = get_artist_similarity(u1_a, u2_a, timeframe)
        tf_points += mu_weights['artist'] * calculate_similarity(df_artist)
        similar_artists = similar_artists.append(df_artist.loc[df_artist['points'] > 0])
        # Track
        df_track = get_track_similarity(u1_t, u2_t, timeframe)
        tf_points += mu_weights['track'] * calculate_similarity(df_track)
        similar_tracks = similar_tracks.append(df_track.loc[df_track['points'] > 0])
        # Genre
        df_genre = get_genre_similarity(u1_g, u2_g, timeframe)
        tf_points += mu_weights['genre'] * calculate_similarity(df_genre)
        similar_genres = similar_genres.append(df_genre.loc[df_genre['points'] > 0])
        # Features
        tf_points += mu_weights['feature'] * calculate_feature_similarity(u1_m, u2_m)
        # Timeframe overall points
        tf_points /= sum(mu_weights.values())
        print('{} term music taste similarity: {:.2f}'.format(timeframe, tf_points * 100))
        final_points += tf_weights[timeframe] * tf_points

    final_points /= sum(tf_weights.values())
    print('Overall music taste similarity: {:.2f}'.format(final_points * 100))
    
    return final_points, users, similar_artists, similar_tracks, similar_genres

def get_similar_artists(df_a):
    engine = create_engine(DATABASE_URL)
    artists = pd.read_sql_query(similar_artists_query, engine, params={'artist_ids': tuple(df_a['artist_id'].tolist())})
    engine.dispose()
    df = df_a.merge(artists, on=['artist_id'])
    return df.sort_values(['timeframe', 'points'], ascending=False)

def get_similar_tracks(df_t):
    engine = create_engine(DATABASE_URL)
    tracks = pd.read_sql_query(similar_tracks_query, engine, params={'track_ids': tuple(df_t['track_id'].tolist())})
    engine.dispose()
    df = df_t.merge(tracks, on=['track_id'])
    return df.sort_values(['timeframe', 'points'], ascending=False)

def get_artist_similarity(u1, u2, timeframe='Long'):
    df1 = u1.loc[u1['timeframe'] == timeframe]
    df2 = u2.loc[u2['timeframe'] == timeframe]
    df = df1.merge(df2, on=['artist_id', 'timeframe'], how='outer').fillna(0)
    df['base'] = calculate_points(df[df[['rank_x', 'rank_y']] > 0].min(axis=1))
    df.loc[(df['rank_x'] != 0) & (df['rank_y'] != 0), 'points'] = calculate_points(df[['rank_x', 'rank_y']].max(axis=1))
    df['points'] = df['points'].fillna(0)
    # df = df.rename(columns={'rank_x': u1['user_id'].unique()[0], 'rank_y': u2['user_id'].unique()[0]})
    return df

def get_track_similarity(u1, u2, timeframe='Long'):
    df1 = u1.loc[u1['timeframe'] == timeframe]
    df2 = u2.loc[u2['timeframe'] == timeframe]
    df = df1.merge(df2, on=['track_id', 'timeframe'], how='outer').fillna(0)
    df['base'] = calculate_points(df[df[['rank_x', 'rank_y']] > 0].min(axis=1))
    df.loc[(df['rank_x'] != 0) & (df['rank_y'] != 0), 'points'] = calculate_points(df[['rank_x', 'rank_y']].max(axis=1))
    df['points'] = df['points'].fillna(0)
    # df = df.rename(columns={'rank_x': u1['user_id'].unique()[0], 'rank_y': u2['user_id'].unique()[0]})
    return df

def get_genre_similarity(u1, u2, timeframe='Long'):
    df1 = u1.loc[u1['timeframe'] == timeframe]
    df2 = u2.loc[u2['timeframe'] == timeframe]
    df = df1.merge(df2, on=['genre', 'timeframe'], how='outer').fillna(0)
    df['base'] = calculate_points(df[df[['rank_x', 'rank_y']] > 0].min(axis=1))
    df.loc[(df['rank_x'] != 0) & (df['rank_y'] != 0), 'points'] = calculate_points(df[df[['rank_x', 'rank_y']] > 0].max(axis=1))
    df['points'] = df['points'].fillna(0)
    # df = df.rename(columns={'rank_x': u1['user_id'].unique()[0], 'rank_y': u2['user_id'].unique()[0]})
    return df.sort_values(['timeframe', 'points'], ascending=False)

def calculate_similarity(df):
    return round(df.sum()['points'] / df.sum()['base'], 4)

def calculate_feature_similarity(u1, u2, timeframe='Long'):
    features1 = u1.loc[u1['timeframe'] == timeframe].drop(columns=['user_id', 'timeframe']).values.tolist()[0]
    features2 = u2.loc[u2['timeframe'] == timeframe].drop(columns=['user_id', 'timeframe']).values.tolist()[0]
    pointss = []
    for i in range(len(features1)):
        f1 = abs(features1[i])
        f2 = abs(features2[i])
        pointss.append(min(f1, f2) / max(f1, f2))
    return round(sum(pointss) / len(pointss), 4)

def calculate_points(rank, weight=16, shift=4):
    return weight / ((0.1 * rank + shift) ** 2) 