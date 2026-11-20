import requests,uuid

def test_ask_500_when_db_auth_fails(bad_api_client):
    #bad_api_client就是bad_server返回的c，也就是ApiClient的实例
    # 可以调用get和post方法拿到返回结果
    rid = f"test-server-error-ask-{uuid.uuid4().hex}"
    r = bad_api_client.post("/ask", json={"question": "直角三角形"},
                            headers={"X-Request-ID": rid})
#这个r就相当于我们手动打开docs时看到的东西，需要输入才有结果
    print(r.status_code, r.text)
    assert r.status_code == 500
    assert r.elapsed.total_seconds() < 6
    

def test_history_500_when_db_auth_fails(bad_api_client):
    rid = f"test-server-error-history-{uuid.uuid4().hex}"
    r = bad_api_client.get("/history",headers={"X-Request-ID": rid})
    assert r.status_code == 500

def test_health_200_when_db_auth_fails(bad_api_client):
    r = bad_api_client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "OK"}