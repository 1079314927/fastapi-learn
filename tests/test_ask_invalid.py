import pytest

@pytest.mark.parametrize("body,rid",[
    ("","test-invalid-1"),
    ("   ","test-invalid-2")
])
def test_empty_question(api_client,body,rid):
    r=api_client.post("/ask",json={"question":body},headers={"X-Request-ID":rid})
    assert r.status_code==400
    assert r.json()== {"error": "question不能为空"}



@pytest.mark.parametrize("body,rid",[
    (123,"test-invalid-3"),
    (["a"],"test-invalid-4")
])
def test_question_type(api_client,body,rid):
    r=api_client.post("/ask",json={"question":body},headers={"X-Request-ID":rid})
    assert r.status_code==422
    detail=r.json()["detail"]
    assert detail[0]["type"] == "string_type"
