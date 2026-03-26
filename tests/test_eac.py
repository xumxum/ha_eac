# tests/test_eac.py

from dotenv import load_dotenv
import os
import pytest
from eac import EACClient

@pytest.fixture
def client():
    load_dotenv()
    username = os.getenv("MY_USERNAME")
    password = os.getenv("MY_PASSWORD")
    return EACClient(username, password)

def test_eac_client_init(client):
    assert client is not None
    # assert client.username == "user"
    # assert client.password == "pass"