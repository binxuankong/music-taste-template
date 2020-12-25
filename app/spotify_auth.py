import base64
import json
import requests

SPOTIFY_URL_AUTH = "https://accounts.spotify.com/authorize/?"
SPOTIFY_URL_TOKEN = "https://accounts.spotify.com/api/token/"
RESPONSE_TYPE = "code"
HEADER = "application/x-www-form-urlencoded"
REFRESH_TOKEN = ""

def get_auth(client_id, redirect_uri, scope):
    data = "{}client_id={}&response_type={}&redirect_uri={}&scope={}".\
        format(SPOTIFY_URL_AUTH, RESPONSE_TYPE, client_id, redirect_uri, scope)
    return data

def get_token(code, client_id, client_secret, redirect_uri):
    body = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    encoded = base64.encode("{}:{}".format(client_id, client_secret))
    headers = {'Content-Type': HEADER, 'Authorization': "Basic {}".format(encoded)}
    post = requests.post(SPOTIFY_URL_TOKEN, params=body, headers=headers)
    return handle_token(json.loads(post.text))

