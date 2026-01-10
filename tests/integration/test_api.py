import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test dashboard loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'CloudOptima' in response.data

def test_api_data(client):
    """Test API returns JSON"""
    response = client.get('/api/data')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'resources' in data
    assert 'scan_time' in data

def test_scan_endpoint(client):
    """Test scan trigger"""
    response = client.post('/api/scan')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] in [True, False]