import os
from sqlalchemy import create_engine
from app.spotifunc import get_user_df, get_recently_played_df, get_current_playlists_df, get_top_artists_df, get_top_tracks_df

TABLES = ['Users', 'RecentlyPlayed', 'CurrentPlaylists', 'TopArtists', 'TopTracks']

def sync_all_data(sp):
    DATABASE_URL = os.environ.get('DATABASE_URL')
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
        user_id = df['user_id'][0]
        delete_user_data(user_id, table, engine)
        insert_new_data(df, table, engine)

def delete_user_data(user_id, table, engine):
    engine.execute('DELETE FROM "{}" WHERE user_id = %(user_id)s'.format(table), user_id=user_id)

def insert_new_data(df, table, engine):
    df.to_sql(table, engine, index=False, if_exists='append')