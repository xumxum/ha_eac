# tests/test_eac.py

from dotenv import load_dotenv
import os
import pytest
from eac import EACClient
from pprint import pprint

@pytest.fixture
def client():
    load_dotenv()
    username = os.getenv("EAC_USERNAME")
    password = os.getenv("EAC_PASSWORD")
    if not username or not password:
        pytest.skip("EAC_USERNAME and EAC_PASSWORD must be set in .env or environment")
    return EACClient(username, password)

def test_eac_client_init(client):
    assert client is not None
    # assert client.username == "user"
    # assert client.password == "pass"

@pytest.mark.integration
def test_eac_fetch_data(client):
    # Replace fetch_data() with the actual method name on EACClient (e.g. login(), get_meter_data(), etc.)
    data = client.fetchMetersData()
    pprint(data)
    assert data is not None
    assert data.spId is not None
    assert data.imp is not None