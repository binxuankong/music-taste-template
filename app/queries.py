user_update_query = """
UPDATE "Users"
SET display_name = %(display_name)s, spotify_url = %(spotify_url)s, image_url = %(image_url)s,
    followers = %(followers)s, last_updated = %(last_updated)s
WHERE user_id = %(user_id)s
"""

user_query = """
SELECT *
FROM "Users" u
WHERE u.user_id = %(user_id)s
"""

top_artists_query = """
SELECT ta.rank, ta.artist_id, ta.timeframe, a.artist, a.genres, a.artist_url, a.artist_image, a.popularity
FROM "TopArtists" ta 
JOIN "Artists" a 
ON ta.artist_id = a.artist_id
WHERE ta.user_id = %(user_id)s
ORDER BY ta.timeframe, ta.rank
"""

top_tracks_query = """
SELECT tt.rank, tt.track_id, tt.timeframe, t.track, t.artists, t.album, t.album_image, t.release_date, t.track_url
FROM "TopTracks" tt
JOIN "Tracks" t
ON tt.track_id = t.track_id
WHERE tt.user_id = %(user_id)s
ORDER BY tt.timeframe, tt.rank
"""

top_genres_query = """
SELECT *
FROM "TopGenres" tg
WHERE tg.user_id = %(user_id)s
"""

music_features_query = """
SELECT *
FROM "MusicFeatures" mf
WHERE mf.user_id = %(user_id)s
"""

artists_update_query = """
UPDATE "Artists" as a
SET genres = ta.genres, artist_image = ta.artist_image, artist_url = ta.artist_url, popularity = ta.popularity 
FROM "TempArtists" as ta
WHERE a.artist_id = ta.artist_id
"""

tracks_update_query = """
UPDATE "Tracks" as t
SET album_image = tt.album_image, track_url = tt.track_url 
FROM "TempTracks" as tt
WHERE t.track_id = tt.track_id 
"""