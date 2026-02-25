from unittest.mock import patch

def test_login_redirects(client):
    with patch("token_.get_oauth") as mock_oauth:
        mock_oauth.return_value.get_authorize_url.return_value = "http://spotify-login"

        response = client.get("/")

        assert response.status_code == 302
        assert "spotify-login" in response.location

def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302

def test_stats_route_requires_login(client):
    response = client.get("/stats/artists/long_term")
    assert response.status_code == 302