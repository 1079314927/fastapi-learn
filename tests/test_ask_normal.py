import uuid
#①命中     → 走"查到了"的分支
def test_ask_normal(api_client):
    r = api_client.post("/ask", json={"question": "直角三角形"},
                        headers={"X-Request-ID": "test-normal-1"})
    assert r.status_code==200
    body=r.json()
    assert body["matched"] is True
    assert set(body.keys())== {"answer","common_mistake","matched","question"}
    assert isinstance(body["answer"],str) and body["answer"]


#②未命中   → 走"没查到"的分支
def test_ask_not_found(api_client):
    r = api_client.post("/ask", json={"question": "不存在的题xyz"},
                        headers={"X-Request-ID": "test-normal-2"})
    assert r.status_code==200
    body=r.json()
    assert body["matched"] is False
    assert set(body.keys())== {"matched","answer"}
    assert body["answer"]=="题库暂未收录该题"


#③特殊字符 → 走"输入脏"的分支
def test_ask_special_chars(api_client):
    r = api_client.post("/ask", json={"question": "直角三角形 <&% 测试"},
                        headers={"X-Request-ID": "test-normal-3"})
    assert r.status_code == 200 
    body = r.json()
    assert "matched" in body
    assert isinstance(body["matched"], bool)


def test_history(api_client):
    q = f"test-history-{uuid.uuid4().hex}"#造一串独有问题文字（记得 `import uuid`）
    r0 = api_client.post("/ask", json={"question": q},
                        headers={"X-Request-ID": "test-history-1"})
    assert r0.status_code == 200

    r = api_client.get("/history", 
                        headers={"X-Request-ID": "test-history-1"})
    assert r.status_code == 200

    body = r.json()    
    assert isinstance(body, list)
    qs = [item["question"] for item in body]
    assert q in qs
    target = [item for item in body if item["question"] == q][0]
    assert set(target.keys()) == {"id","question","matched","created_at"}