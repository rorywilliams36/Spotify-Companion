# Spotify Companion/Analytics

Application using Python Flask to view and create playlists based on your spotify listening stats by using [Spotify's API]{https://developer.spotify.com/documentation/web-api}

## To Run
1. First go to [Spotify Dashboard](https://developer.spotify.com/dashboard) and login into your account
2. Create an app, set the callback url to http://127.0.0.1:5000/callback and copy/paste your client id and client secret into the .env file
3. install the requirements using `pip install -r requirements.txt` in your terminal
4. Navigate to the folder that contains this project and run `python main.py`
5. The app will be running locally at http://127.0.0.1:5000/
