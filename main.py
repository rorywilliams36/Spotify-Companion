from endpoints import *

from dotenv import load_dotenv
from requests import post, get
import os
import time
import base64
import json
import secrets

from flask import Flask, url_for, session, redirect, request, render_template
from flask_caching import Cache

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load client id and secret from env file
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
REDIRECT_URL = "http://127.0.0.1:5000/callback"
HOME = 'http://127.0.0.1:5000'

# Setup app and cache configs
config = { "DEBUG": True,          
    "CACHE_TYPE": "SimpleCache", 
    "CACHE_DEFAULT_TIMEOUT": 1800,
    "SESSION_COOKIE_NAME": "Spotify Cookie"
} 

# Init app
app = Flask(__name__)
app.config.from_mapping(config)
app.secret_key = secrets.token_hex() 
cache = Cache(app)

@app.route('/')
# login to user profile
def login():
    # Sends Ouath object to spotify for login
    login_url = get_oauth().get_authorize_url()
    return redirect(login_url)

@app.route('/callback')
def callback_page():
    session.clear()
    # Get result from login
    code = request.args.get('code')
    state = request.args.get('state')
    # Creates access token
    token = access_token(code, state)
    # Store token in session cookie
    session['token_info'] = token
    # Store User's API data in cache
    store_data()
    # Moves onto main page
    return redirect(url_for('profile', _external=True))

@app.route('/dashboard')
def profile():
    # Check session key and cache exists
    if session.get('token_info') and cache.get('user_'):
        # Get relevant data from cache for profile/dashboard page
        user_data = cache.get('user_')
        profile = user_data['profile']
        tracks = user_data['tracks']['long_term'][:10]
        artists = user_data['artists']['long_term'][:10]
        return render_template('dashboard.html', profile=profile, artists=artists, tracks=tracks)
    return redirect(url_for('login'))

@app.route('/stats') 
def stats(item_type: str = 'artists', time_range: str = 'long_term'):
    pass


@app.route('/error')
def error():
    pass

# Stores all relevant User API data in the cache
@cache.cached(key_prefix='user_')
def store_data():
    user_data = get_full_data()
    return user_data


def access_token(code, state):
    # Checks if successful login retruned correct results
    if code == None:
        return redirect(url_for('login'))
        
    auth_base64 = encode_client_creds()

    # Format for request to get access token
    url = "https://accounts.spotify.com/api/token"

    header = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "code" : code,
        "grant_type": "authorization_code",
        "redirect_uri" : url_for('callback_page', _external=True), 
        }

    res = post(url, headers=header, data=data)
    token = json.loads(res.content)
    return token

# Refreshes token after time expiry
def refresh_token():
    token = session['token_info']

    auth_base64 = encode_client_creds()

    url = 'https://accounts.spotify.com/api/token' 
    headers = {
        'content-type' : 'application/x-www-form-urlencoded', 
        'Authorization' : 'Basic' + auth_base64
    }
    data = {
        'grant-type' : 'refresh_token',
        'refresh-token' : token
    }
    
    res = post(url, headers=header, data=data)
    json_result = json.loads(res.content)
    token = json_result["access_token"]
    session['token_info'] = token

    # Reinstate cache
    cache.clear()
    store_data()

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
        scope = 'playlist-modify-public playlist-modify-private user-top-read user-read-recently-played user-library-read user-read-email user-read-private'
    )




if __name__ == "__main__":
    app.run(debug=True)