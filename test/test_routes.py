from unittest.mock import patch

def test_login_redirects(client):
    with patch("token_.get_oauth") as mock_oauth:
        mock_oauth.return_value.get_authorize_url.return_value = "http://spotify-login"

        response = client.get("/")

        assert response.status_code == 302
        assert "spotify-login" in response.location

def test_dashboard_route(client):
    response = client.get("/dashboard")
    assert response.status_code == 302

def test_stats_route(client):
    response = client.get("/stats/artists/long_term")
    assert response.status_code == 302

def test_playlist_route(client):
    response = client.get("/playlist")
    assert response.status_code == 302

def test_create_playlist(client):
    response = client.post("/create-playlist", 
    data = {
        "time_range" : 'long_term',
        "playlist_size" : 10, 
        "playlist_name" : "My Top Songs", 
        "public" : False,
        "playlist_description" : "my songs"
    })
    assert response.status_code == 302