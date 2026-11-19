def test_empty_question(api_client):
    r=api_client.post("/ask",json={"question": ""},headers={"X-Request-ID":"test-invalid-1"})
    assert r.status_code==400
    assert r.json()== {"error": "question不能为空"}


def test_blank_question(api_client):
    r=api_client.post("/ask",json={"question": "   "},headers={"X-Request-ID":"test-invalid-2"})
    assert r.status_code==400
    assert r.json()== {"error": "question不能为空"}

def test_question_number(api_client):
    r=api_client.post("/ask",json={"question":123},headers={"X-Request-ID":"test-invalid-3"})
    assert r.status_code==422
    detail=r.json()["detail"]
    assert detail[0]["type"] == "string_type"

def test_question_list(api_client):
    r=api_client.post("/ask",json={"question":["a"]},headers={"X-Request-ID":"test-invalid-4"})
    assert r.status_code==422
    detail=r.json()["detail"]
    assert detail[0]["type"] == "string_type"

def test_too_long_question(api_client):
    r=api_client.post("/ask",json={"question":"直" * 10000},headers={"X-Request-ID":"test-invalid-5"})
    assert r.status_code==200
    body=r.json()
    assert body["matched"]is False