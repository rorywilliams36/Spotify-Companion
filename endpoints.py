import json
import time

from requests import get, post
from flask import session

import token_

class SpotifyClient():

    def get_token(self):
        ''' Gets token from session cookie '''
        if 'token_info' not in session:
            return None

        if time.time() > session['token_info']['expires_in']:
            session['token_info'] = token_.get_refresh_token()

        return session['token_info']['access_token']

    def get_profile(self):
        ''' returns JSON payload (dict) for the current user's profile '''
        url = "https://api.spotify.com/v1/me"

        res = self.place_get_request(url)

        json_result = json.loads(res.content)
        return json_result

    def get_top_item(self, item_type: str = 'tracks', limit: int = 2, time_range: str = 'short_term', offset: int = 0):
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

        res = self.place_get_request(url)

        if res.status_code == 200:
            json_result = json.loads(res.content)
            return res.status_code, json_result['items']
        return res.status_code, None


    def get_current_playlists(self, limit: int = 2, offset: int = 0):
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

        res = self.place_get_request(url)

        if res.status_code == 200:
            json_result = json.loads(res.content)
            return res.status_code, json_result
        return res.status_code, None

    def get_saved_tracks(self, limit: int = 2, offset: int = 0):    
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

        res = self.place_get_request(url)

        if res.status_code == 200:
            json_result = json.loads(res.content)
            return res.status_code, json_result['items']
        return res.status_code, None

    def store_api_data(self):
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
        user_data['profile'] = self.get_profile()

        # Calls API for each time range then gets and sets the user's tracks and artists
        for tr in time_ranges:
            a_status, tracks = self.get_top_item(item_type='tracks', limit=50, time_range=tr)
            t_status, artists = self.get_top_item(item_type='artists', limit=50, time_range=tr)

            user_data['tracks'][tr] = tracks
            user_data['artists'][tr] = artists

        return user_data

    def create_playlist(self, name, description, public):
        '''
        Creates spotify playlist using post request

        Params:
            name: string user's inputted name of playlist
            description: string user's description of playlist
            public: boolean stating if playlist is public or private

        Returns:
            playlist_id: spotify_id of the newly created playlist (string)
        '''
        url = 'https://api.spotify.com/v1/me/playlists'

        data = {
            "name" : name,
            "description" : description, 
            "public" : public, 
            "collaborative" : False
        }

        res = self.place_post_request(url, data)

        if res.status_code == 201:
            playlist = json.loads(res.content)
            playlist_id = playlist['id']
            return playlist_id
        return None

    def add_playlist(self, tracks, playlist_id, size):
        '''
        Adds songs to a requested playlist using the track ids

        params:
            tracks: array of spotify track objects to be added to the playlist
            playlist_id: spotify id of the chosen playlist (string)
            size: integer (0-50) showing number of tracks to be added to the playlist

        Return:
            status code of post request (200/201 == success)
        '''
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/items'
        track_uris = []

        for track in tracks[:size]:
            track_uris.append(f'spotify:track:{track['id']}')

        data = {
            'uris' : track_uris
        }
        
        res = self.place_post_request(url, data)
        return res.status_code

    def place_post_request(self, url, data):
        '''
        Sends Post Requests

        Params:
            url: String of the api endpoint
            data: Data (dict/json) sent to endpoint

        Return:
            Response object containing the relevant content
        '''
        token = self.get_token()

        header = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + token
        }
        return post(url, headers=header, json=data, timeout=30)

    def place_get_request(self, url):
        '''
        Sends Get Requests

        Params:
            url: String of the api endpoint

        Return:
            Response object containing the relevant content
        '''
        token = self.get_token()

        header = {
            "Authorization": "Bearer " + token
        }
        return get(url, headers=header, timeout=10)

# Lazy Load
spotify = SpotifyClient()
