from unittest.mock import patch
from main import fetch_api_data, spotify, cache

# Test cache returns correct data
def test_fetch_is_cached(client):
    with client.application.test_request_context():

        with patch("main.spotify.store_api_data") as mock:
            mock.return_value = {'username' : 'user123'}

            res1 = fetch_api_data()
            res2 = fetch_api_data()

            mock.assert_called_once()

            assert res1 == res2

# check cache stores data
def test_cache_store(client):
    with client.application.test_request_context():
        fetch_api_data()
        cached = cache.get('user_')
        assert cached is not None