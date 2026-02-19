import os
import base64
import json

from dotenv import load_dotenv
from requests import post

from flask import url_for, session, redirect

from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def access_token(code):
    # Checks if successful login retruned correct results
    if code is None:
        return redirect(url_for('login'))
        
    # Format for request to get access token
    url = "https://accounts.spotify.com/api/token"

    data = {
        "code" : code,
        "grant_type" : "authorization_code",
        "redirect_uri" : url_for('callback_page', _external=True)
    }

    # post request for access token
    res = place_post_request(url, data)
    token = json.loads(res.content)
    return token

# Refreshes token after time expiry
def refresh_token():
    token = session['token_info']

    # Format Request
    url = 'https://accounts.spotify.com/api/token' 

    data = {
        'grant-type' : 'refresh_token',
        'refresh-token' : token
    }

    # Post request and save token
    res = place_post_request(url, data)

    json_result = json.loads(res.content)
    token = json_result["access_token"]
    session['token_info'] = token

    # Reinstate cache
    cache.clear()
    main.fetch_api_data()

    return json_result

# Acquires the access token from the session and calls refresh in case of expiry
def get_access_token():
    if not session['token_info']:
        return redirect(url_for('login'))
    token_json = session["token_info"]
    token = token_json['access_token']
    expiry = token_json['expires_in']
    if expiry < 120:
        token = refresh_token()
    return token

# Creates utf-8 encoding of client credentials
def encode_client_creds():
    auth_str = client_id + ":" + client_secret
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    return auth_base64

# Creates Auth header for spotify api token
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# Creates Oauth object for access to user's account
def get_oauth():
    return SpotifyOAuth(
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = url_for('callback_page', _external=True), 
        scope = """playlist-modify-public playlist-modify-private 
        user-top-read user-read-recently-played user-library-read
        user-read-email user-read-private"""
    )


def place_post_request(url, data):
    auth_base64 = encode_client_creds()

    headers = {
        'content-type' : 'application/x-www-form-urlencoded', 
        'Authorization' : 'Basic ' + auth_base64
    }

    return post(url, headers=headers, data=data, timeout=10)
