import requests

def test_health(base_url):
    r = requests.get(f"{base_url}/health", timeout=10)
    assert r.status_code == 201
    assert r.json() == {"status": "OK"}

def test_health_via_client(api_client):
    r=api_client.get("/health")#这里用session而不是requests
    assert r.status_code == 200
    assert r.json() == {"status": "OK"}

