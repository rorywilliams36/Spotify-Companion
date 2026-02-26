import secrets

from flask import Flask, url_for, session, redirect, request, render_template, flash
from flask_caching import Cache

from endpoints import spotify   # imports class for api calls
import token_   # Code to create and refresh the access token

# Setup app and cache configs
config = { "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 3600,
    "SESSION_COOKIE_NAME": "Spotify Cookie"
} 

# Init app and cache
app = Flask(__name__)
app.config.from_mapping(config)
app.secret_key = secrets.token_hex() 
cache = Cache(app)

@app.before_request
def check_auth():
    public_routes = ["login","callback", "static"]
    protected_routes = ["dashboard", "stats", "playlist", "create_playlist"]

    if request.endpoint in protected_routes:
        token = session.get('token_info') 
        if not token:
            return redirect(url_for('login'))

            if not cache.get('user_'):
                fetch_api_data()
                return redirect(url_for('dashboard'))
    return    

@app.route('/')
def login():
    ''' Login and oauth for user'''
    # Sends Ouath object to spotify for login
    login_url = token_.get_oauth().get_authorize_url()
    return redirect(login_url)

@app.route('/callback')
def callback_page():
    ''' Callback to creat token and fill cache '''
    session.clear()
    # Get result from login
    code = request.args.get('code')

    # state = request.args.get('state')
    # Creates access token
    token = token_.access_token(code)

    # Store token in session cookie
    session['token_info'] = token

    # Store User's API data in cache
    fetch_api_data()
    # Moves onto main page
    return redirect(url_for('dashboard', _external=True))

@app.route('/dashboard')
def dashboard():
    ''' Profile Dashboard Page'''
    # Check session key and cache exists
    # Get relevant data from cache for profile/dashboard page
    user_data = cache.get('user_')
    profile = user_data['profile']
    tracks = user_data['tracks']['long_term'][:10]
    artists = user_data['artists']['long_term'][:10]
    return render_template('dashboard.html', profile=profile, artists=artists, tracks=tracks)


@app.route('/stats/<item_type>/<time_range>') 
def stats(item_type, time_range):
    '''  Page to display user listening stats'''
    try:
        user_data = cache.get('user_')
        # sets default options if none are selected
        if item_type not in ("tracks", "artists"):
            item_type = 'artists'

        if time_range not in ("short_term", "medium_term", "long_term"):
            time_range = 'long_term'
        
        # Gets items and loads page
        items = user_data[item_type][time_range]
        return render_template('stats.html', items=items, item_type=item_type, time_range=time_range)

    except Exception:
        flash('Error loading data')
    
    return redirect(url_for('login'))

@app.route('/playlist')
def playlist():
    ''' Playlist Form '''
    return render_template('playlist.html')

@app.route('/create-playlist', methods=['POST'])
def create_playlist():
    ''' Creates playlist using info from form'''
    user_data = cache.get('user_')

    time_range = request.form["time_range"]
    size = int(request.form["playlist_size"])
    name = str(request.form["playlist_name"])
    public = True if request.form.get("public") else False
    description = str(request.form["playlist_description"])

    tracks = user_data['tracks'][time_range]

    try:
        playlist_id = spotify.create_playlist(name, description, public)
        status = spotify.add_playlist(tracks, playlist_id, size)
        flash('Playlist Successfully Created!')
    except Exception:
        flash('Error Creating Playlist')

    return redirect(url_for('playlist'))
    
@cache.cached(key_prefix='user_', timeout=3600)
def fetch_api_data():
    ''' Stores all relevant User API data in the cache '''
    return spotify.store_api_data()


if __name__ == "__main__":
    app.run(debug=True)
