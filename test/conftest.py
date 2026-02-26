import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    app.config["SERVER_NAME"] ="127.0.0.1:5000"

    with app.test_client() as client:
        with app.app_context():
            yield client