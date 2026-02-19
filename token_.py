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
    ''' Acquires access token to access spotify api '''
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

def refresh_token():
    ''' Refreshes token after time expiry '''

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

def get_access_token():
    '''Acquires the access token from the session and calls refresh in case of expiry'''
    if not session['token_info']:
        return redirect(url_for('login'))
    token_json = session["token_info"]
    token = token_json['access_token']
    expiry = token_json['expires_in']
    if expiry < 120:
        token = refresh_token()
    return token

def encode_client_creds():
    ''' Creates utf-8 encoding of client credentials '''
    auth_str = client_id + ":" + client_secret
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    return auth_base64

def get_oauth():
    ''' Creates Oauth object for access to user's account '''
    return SpotifyOAuth(
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = url_for('callback_page', _external=True), 
        scope = """playlist-modify-public playlist-modify-private 
        user-top-read user-read-recently-played user-library-read
        user-read-email user-read-private"""
    )


def place_post_request(url, data):
    '''
    Sends Post Requests

    Params:
        url: String of the api endpoint
        data: Data (dict/json) sent to endpoint

    Return:
        Response object containing the relevant content
    '''

    # Encodes the client credentials into base64
    auth_base64 = encode_client_creds()

    headers = {
        'content-type' : 'application/x-www-form-urlencoded', 
        'Authorization' : 'Basic ' + auth_base64
    }

    return post(url, headers=headers, data=data, timeout=10)
