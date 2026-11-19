def test_missing_field(api_client):
    r=api_client.post("/ask",json={},headers={"X-Request-ID":"test-missing-1"})
    assert r.status_code==422
    detail = r.json()["detail"]
    assert detail[0]["type"] == "missing"
    assert detail[0]["loc"] == ["body", "question"]

def test_missing_null(api_client):
    r=api_client.post("/ask",json={"question": None},headers={"X-Request-ID":"test-missing-2"})
    assert r.status_code==422
    detail = r.json()["detail"]
    assert detail[0]["type"] == "string_type"
    assert detail[0]["loc"] == ["body", "question"]

def test_missing_no_body(api_client):
    r=api_client.post("/ask",headers={"X-Request-ID":"test-missing-3"})
    assert r.status_code==422
    detail = r.json()["detail"]
    assert detail[0]["type"] == "missing"
    assert detail[0]["loc"] == ["body"]