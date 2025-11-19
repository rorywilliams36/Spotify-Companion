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

