import sys
import os
import pytest

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pet_search_service.pet_search_service import app  # Import the app object


@pytest.fixture
def client():
    """Create a test client for the app."""
    with app.test_client() as client:
        yield client

def test_search_menu(client):
    """Test the search menu route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Search" in response.data  # Match an actual keyword present in the response

def test_search_pets(client, monkeypatch):
    """Test the search pets route with a mocked API."""
    def mock_get_petfinder_token():
        return "mock_token"
    
    # Correctly target the function in your local module
    monkeypatch.setattr("pet_search_service.pet_search_service.get_petfinder_token", mock_get_petfinder_token)

    response = client.get('/search', query_string={'type': 'dog'})
    assert response.status_code == 200
    assert b"Results" in response.data  # Adjust based on your actual response content

