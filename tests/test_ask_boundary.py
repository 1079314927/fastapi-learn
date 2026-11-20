# 服务当前没有 question 长度上限，4999/5000/5001 全部返回 200；
# 这是校验缺口，先锁现状。等加了 max_length=5000 后，5001 应改为断言 400。



def test_question_len_4999(api_client):
    r = api_client.post("/ask", json={"question":"直"*4999},
                        headers={"X-Request-ID": "test-boundary-1"})
    assert r.status_code==200
    body=r.json()
    assert body["matched"] is False
    assert set(body.keys())== {"matched","answer"}
    assert body["answer"]=="题库暂未收录该题"

def test_question_len_5000(api_client):
    r = api_client.post("/ask", json={"question":"直"*5000},
                        headers={"X-Request-ID": "test-boundary-2"})
    assert r.status_code==200
    body=r.json()
    assert body["matched"] is False
    assert set(body.keys())== {"matched","answer"}
    assert body["answer"]=="题库暂未收录该题"

def test_question_len_5001(api_client):
    r = api_client.post("/ask", json={"question":"直"*5001},
                        headers={"X-Request-ID": "test-boundary-3"})
    assert r.status_code==200
    body=r.json()
    assert body["matched"] is False
    assert set(body.keys())== {"matched","answer"}
    assert body["answer"]=="题库暂未收录该题"