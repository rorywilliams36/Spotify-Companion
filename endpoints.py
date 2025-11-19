from main import get_access_token, get_auth_header

import json
from requests import post, get
from flask import Flask, url_for, session, redirect, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# returns json payload for the current user's profile
def get_profile():
    url = "https://api.spotify.com/v1/me"
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header)
    json_result = json.loads(res.content)
    return json_result

def get_top_item(item_type: str = 'tracks', limit: int = 2, time_range: str = 'medium_term'):
    url = f'https://api.spotify.com/v1/me/top/{item_type}'
    token = get_access_token()
    auth_header = get_auth_header(token)
    data = {
        'limit' : limit,
        'time_range' : time_range
    }
    print(token)
    res = get(url, headers=auth_header)
    print(res.status_code)
    print(res.content)
    if res.status_code == 200:
        json_result = json.loads(res.content)
        return json_result
    return None


