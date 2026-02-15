import json
from requests import get

from main import get_access_token, get_auth_header

# returns JSON payload (dict) for the current user's profile
def get_profile():
    url = "https://api.spotify.com/v1/me"
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header, timeout=10)
    json_result = json.loads(res.content)
    return json_result


def get_top_item(item_type: str = 'tracks', limit: int = 2, time_range: str = 'short_term', offset: int = 0):
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
    limit = min(limit, 50)
    url = f'https://api.spotify.com/v1/me/top/{item_type}?limit={limit}&time_range={time_range}&offset={offset}'
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header, timeout=10)
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
    limit = min(limit, 50)
    url = f'https://api.spotify.com/v1/me/playlists?limit={limit}&offset={offset}'
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header, timeout=10)
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
    limit = min(limit, 50)
    url = f'https://api.spotify.com/v1/me/tracks?limit={limit}&offset={offset}'
    token = get_access_token()
    auth_header = get_auth_header(token)
    res = get(url, headers=auth_header, timeout=10)
    if res.status_code == 200:
        json_result = json.loads(res.content)
        return res.status_code, json_result['items']
    return res.status_code, None

def store_api_data():
    '''
    Retrives and formats the user's spotify data using relevant api calls

    Returns:
        JSON/Dict of the all user's spotify 'top items' and 'profile' data

        Format:
            {"profile" : {}, "artists" : {"long_term" : [], "medium_term" : [] , "short_term" : []}, 
            "tracks" :  {"long_term" : [], "medium_term" : [] , "short_term" : []}}
    '''
    time_ranges = ["long_term" , "medium_term", "short_term"]
    # Setup dict with relevant keys for eas of access in the cache
    user_data = {"profile" : {}, "artists" : {"long_term" : [], "medium_term" : [] , "short_term" : []}, 
    "tracks" :  {"long_term" : [], "medium_term" : [] , "short_term" : []}}

    # Get the user's profile data
    user_data['profile'] = get_profile()

    # Calls API for each time range then gets and sets the user's tracks and artists
    for tr in time_ranges:
        a_status, tracks = get_top_item(item_type='tracks', limit=50, time_range=tr)
        t_status, artists = get_top_item(item_type='artists', limit=50, time_range=tr)

        user_data['tracks'][tr] = tracks
        user_data['artists'][tr] = artists

    return user_data

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

# Returns dictionary containing counts for genres
def extract_genres(artists):
    genre_count = {}

    for artist in artists:
        genres = artist['genres']
        for genre in genres:
            if genre not in genre_count:
                genre_count[genre] = 1
            else:
                genre_count[genre] += 1

    return dict(sorted(genre_count.items(), reverse=True, key=lambda item: item[1]))

