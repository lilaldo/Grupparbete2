from application.app import app  # Importerar Flask app från application.
import pytest

# Skapa en "fixture" för att tillhandahålla en testklient för Flask-appen
@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

# Test för '/reseplanerare' rutten
def test_reseplanerare(client):
    response = client.get('/reseplanerare')
    assert response.status_code == 200
  

# Test för '/search' rutten
def test_search(client):
    response = client.get('/search')
    assert response.status_code == 200
    

# Test för '/realtid' rutten
def test_realtid(client):
    response = client.get('/realtid')
    assert response.status_code == 200
   

# Test för  '/realtid_result' rutten
def test_realtid_result(client):
    response = client.get('/realtid_result')
    assert response.status_code == 200
    
# Test för '/priser' rutten
def test_priser(client):
    response = client.get('/priser')
    assert response.status_code == 200
  

# Test för '/trafiklage' rutten
def test_trafiklage(client):
    response = client.get('/trafiklage')
    assert response.status_code == 200
   
