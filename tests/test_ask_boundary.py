# 服务当前没有 question 长度上限，4999/5000/5001 全部返回 200；
# 这是校验缺口，先锁现状。等加了 max_length=5000 后，5001 应改为断言 422。
#业务不合法 → 400；字段不合规 → 422。
import pytest

@pytest.mark.parametrize("body,rid",[
    ("直"*4999,"test-boundary-1"),
    ("直"*5000,"test-boundary-2"),
    ("直"*5001,"test-boundary-3"),
    ("直"*10000,"test-boundary-4"),
])
def test_too_long_question(api_client,body,rid):
    r = api_client.post("/ask", json={"question":body},
                        headers={"X-Request-ID": rid})
    assert r.status_code==200
    rsp=r.json()
    assert rsp["matched"] is False
    assert set(rsp.keys())== {"matched","answer"}
    assert rsp["answer"]=="题库暂未收录该题"


