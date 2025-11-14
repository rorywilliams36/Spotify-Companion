from dotenv import load_dotenv
from requests import post, get
import os
import base64
import json
import secrets
from flask import Flask, url_for, session, redirect, request

import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
REDIRECT_URL = "http://127.0.0.1:5000/callback"

app = Flask(__name__)
app.config["SESSION_COOKIE_NAME"] = "Spotify Cookie"
app.secret_key = secrets.token_hex()

@app.route('/')
# login to user profile
def login():
    print('login')
    login_url = get_oauth().get_authorize_url()
    return redirect(login_url)

@app.route('/callback')
def callback_page():
    print('Callback')
    session.clear()
    code = request.args.get('code')
    state = request.args.get('state')
    token_info = access_token(code, state)
    return redirect(url_for('view'))

@app.route('/view')
def view():
    print('Oauth Success')
    exit

def access_token(code, state):
    if state == None or code == None:
        return redirect('/')


    auth_str = client_id + ":" + client_secret
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"

    header = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "code" : code,
        "grant_type": "client_credentials"
        }

    res = post(url, headers=header, data=data)
    json_result = json.loads(res.content)
    token = json_result["access_token"]

    return token

# Spotify API token
def get_token():
    auth_str = client_id + ":" + client_secret
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"

    header = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    res = post(url, headers=header, data=data)
    json_result = json.loads(res.content)
    token = json_result["access_token"]
    return token

# Creates Auth header for spotify api token
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# Creates access token for the user's data
def get_oauth():
    return SpotifyOAuth(
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = url_for('callback_page', _external=True), 
        scope = 'user-library-read playlist-modify-public playlist-modify-private'
    )

app.run()