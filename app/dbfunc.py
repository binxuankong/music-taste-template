from app.queries import artists_update_query, tracks_update_query, artists_insert_query, tracks_insert_query

def sync_data(df, table, engine):
    if len(df) > 0:
        delete_user_data(df, table, engine)
        insert_new_data(df, table, engine)

def update_artists_and_tracks(engine):
    engine.execute(artists_update_query)
    engine.execute(tracks_update_query)
    engine.execute(artists_insert_query)
    engine.execute(tracks_insert_query)

def delete_user_data(df, table, engine):
    user_id = df['user_id'].unique()[0]
    # timeframe = df['timeframe'][0]
    # engine.execute('DELETE FROM "{}" WHERE user_id = %(user_id)s AND timeframe = %(timeframe)s'.format(table), user_id=user_id, timeframe=timeframe)
    engine.execute('DELETE FROM "{}" WHERE user_id = %(user_id)s'.format(table), user_id=user_id)

def insert_new_data(df, table, engine):
    df.to_sql(table, engine, index=False, if_exists='append')

def top_to_dict(top_df):
    top_dict = {}
    top_dict[0] = top_df.loc[top_df['timeframe'] == 0].to_dict('records')
    top_dict[1] = top_df.loc[top_df['timeframe'] == 1].to_dict('records')
    top_dict[2] = top_df.loc[top_df['timeframe'] == 2].to_dict('records')
    return top_dict