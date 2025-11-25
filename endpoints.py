from main import get_access_token, get_auth_header

import json
from requests import post, get
from flask import Flask, url_for, session, redirect, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# returns JSON payload (dict) for the current user's profile
def get_profile():
    url = "https://api.spotify.com/v1/me"
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header)
    json_result = json.loads(res.content)
    return json_result


def get_top_item(item_type: str = 'tracks', limit: int = 2, time_range: str = 'medium_term', offset: int = 0):
    '''
    Returns the top tracks or artists the user listens to

    Params:
        item_type: string, either 'tracks' or 'artists'
        limit: integer of the number items to be returned
        time_range: string displaying how far bakc to grab data from ('short_term', 'medium_term', 'long_term')
        offset: int

    Returns:
        JSON payload (dict) of the top items recieved from the endpoint
    '''
    url = f'https://api.spotify.com/v1/me/top/{item_type}?limit={limit}&time_range={time_range}&offset={offset}'
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header)
    if res.status_code == 200:
        json_result = json.loads(res.content)
        return res.status_code, json_result['items']
    return res.status_code, None


def get_current_playlists(limit: int = 2, offset: int = 0):
    '''
    Returns the current users' saved playlists

    Params:
        limit: integer of the number items to be returned
        offset: int

    Returns:
        JSON payload (dict) of the playlists recieved from the endpoint
    '''
    url = f'https://api.spotify.com/v1/me/playlists?limit={limit}&offset={offset}'
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header)
    if res.status_code == 200:
        json_result = json.loads(res.content)
        return res.status_code, json_result
    return res.status_code, None

def get_saved_tracks(limit: int = 2, offset: int = 0):    
    '''
    Returns the current users' saved/liked songs

    Params:
        limit: integer of the number items to be returned
        offset: int

    Returns:
        JSON payload (dict) of the saved/liked songs recieved from the endpoint
    '''
    url = f'https://api.spotify.com/v1/me/tracks?limit={limit}&offset={offset}'
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header)
    if res.status_code == 200:
        json_result = json.loads(res.content)
        return res.status_code, json_result['items']
    return res.status_code, None

# Returns the top tracks in a dictionary to display easier
def extract_top_tracks(tracks):
    tracks_dict = {"artists" : [], "tracks" : []}

    for track in tracks:
        tracks_dict["artists"].append(track['artists'][0]['name'])
        tracks_dict["tracks"].append(track['name'])

    return tracks_dict

# Returns the top artists in an array
def extract_top_artists(artists):
    artists_arr = []
    
    for artist in artists:
        artists_arr.append(artist['name'])

    return artists_arr