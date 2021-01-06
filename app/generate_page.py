from flask import render_template
from app.dbfunc import get_user_profile, get_top_artists, get_top_tracks, get_top_genres, get_music_features, top_to_dict
from app.vizfunc import plot_genre_chart, plot_mood_gauge

def generate_profile_page(user_id, user_profile, is_user=False, public=True):
    if not public:
        return render_template('user.html', public=False, user=user_profile)
    top_artists = get_top_artists(user_id)
    top_tracks = get_top_tracks(user_id)
    top_genres = get_top_genres(user_id)
    music_features = get_music_features(user_id)
    # Mainstream meter
    mainstream_score = int(top_artists['popularity'].mean())
    # To dict format
    top_artists = top_to_dict(top_artists)
    top_tracks = top_to_dict(top_tracks)
    music_features = top_to_dict(music_features)
    # Plot charts
    genre_data = plot_genre_chart(top_genres)
    mood_data = plot_mood_gauge(music_features)
    if is_user:
        return render_template('profile.html', user=user_profile, artists=top_artists, tracks=top_tracks, genres=genre_data, \
                               moods=mood_data, mainstream=mainstream_score)
    else:
        return render_template('user.html', public=True, user=user_profile, artists=top_artists, tracks=top_tracks, genres=genre_data, \
                               moods=mood_data, mainstream=mainstream_score)