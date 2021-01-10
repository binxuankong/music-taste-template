from flask import render_template
from app.dbfunc import get_user_profile, get_top_artists, get_top_tracks, get_top_genres, get_music_features, top_to_dict
from app.vizfunc import calculate_mainstream_score, plot_genre_chart, plot_mood_gauge
from app.comparefunc import compare_users, get_similar_artists, get_similar_tracks

def generate_profile_page(user_id, user_profile, is_user=False, public=True):
    if not public:
        return render_template('profile.html', is_user=False, public=False, user=user_profile)
    top_artists = get_top_artists(user_id)
    top_tracks = get_top_tracks(user_id)
    top_genres = get_top_genres(user_id)
    music_features = get_music_features(user_id)
    # Mainstream meter
    mainstream_score = calculate_mainstream_score(top_artists)
    # To dict format
    top_artists = top_to_dict(top_artists)
    top_tracks = top_to_dict(top_tracks)
    music_features = top_to_dict(music_features)
    # Plot charts
    genre_data = plot_genre_chart(top_genres)
    mood_data = plot_mood_gauge(music_features)
    if is_user:
        return render_template('profile.html', is_user=True, public=True, user=user_profile, artists=top_artists, tracks=top_tracks, \
                               genres=genre_data, moods=mood_data, mainstream=mainstream_score)
    else:
        return render_template('profile.html', is_user=False, public=True, user=user_profile, artists=top_artists, tracks=top_tracks, \
                               genres=genre_data, moods=mood_data, mainstream=mainstream_score)

def generate_match_page(user1, user2):
    s, df_u, df_a, df_t, df_g = compare_users(user1, user2)
    score = round(s * 100, 2)
    users = df_u.to_dict('records')
    similar_artists = top_to_dict(get_similar_artists(df_a))
    similar_tracks = top_to_dict(get_similar_tracks(df_t))
    similar_genres = plot_genre_chart(df_g)
    return render_template('result.html', users=users, score=score, artists=similar_artists, tracks=similar_tracks, genres=similar_genres)
