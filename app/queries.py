user_update_query = """
UPDATE "Users"
SET display_name = %(display_name)s, spotify_url = %(spotify_url)s, image_url = %(image_url)s,
    followers = %(followers)s, last_login = %(last_login)s
WHERE user_id = %(user_id)s
"""