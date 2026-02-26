import json
import time
from unittest.mock import patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import token_

def test_access_token_no_code(client):
    response = token_.access_token(None)

    assert response.status_code == 302

def test_access_token_success(client):
    # Checks return
    # Create fake response for post request
    fake_response = type("Response", (), {})()
    fake_response.content = json.dumps({
        "access_token": "test_access",
        "refresh_token": "test_refresh",
        "expires_in": 3600
    }).encode()

    # returns fake response
    with patch("token_.place_post_request", return_value=fake_response) as mock_post:
        token = token_.access_token("fake_code")

        # checks post request returns fake response
        assert token["access_token"] == "test_access"
        assert token["refresh_token"] == "test_refresh"
        mock_post.assert_called_once()

def test_access_token_sends_correct_data(client):
    # Checks Send
    fake_response = type("Response", (), {})()
    fake_response.content = json.dumps({
        "access_token": "abc",
        "refresh_token": "xyz",
        "expires_in": 3600
    }).encode()

    with patch("token_.place_post_request", return_value=fake_response) as mock_post:
        token_.access_token("my_code")

        args, kwargs = mock_post.call_args

        sent_url = args[0]
        sent_data = args[1]

        assert sent_url == "https://accounts.spotify.com/api/token"
        assert sent_data["code"] == "my_code"
        assert sent_data["grant_type"] == "authorization_code"