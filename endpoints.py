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

def get_top_item(item_type: str = 'tracks', limit: int = 2, time_range: str = 'medium_term', offset: int = 0):
    url = f'https://api.spotify.com/v1/me/top/{item_type}?limit={limit}&time_range={time_range}&offset={offset}'
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header)
    if res.status_code == 200:
        json_result = json.loads(res.content)
        return json_result
    return None


def get_current_playlists(limit: int = 2, offset: int = 0):
    url = f'https://api.spotify.com/v1/me/playlists?limit={limit}&offset={offset}'
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header)
    if res.status_code == 200:
        json_result = json.loads(res.content)
        return json_result
    return None