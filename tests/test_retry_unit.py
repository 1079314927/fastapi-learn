

#前置知识点：
# `pytest.raises` 是 pytest 自带的一个 “**预期出错的容器**”。用 `with` 把它包住一段代码，等于向 pytest 声明：
#  “接下来这几行**一定会抛异常**，我知道。你别把它判成失败，请先看看是不是这个异常。”

# `caplog` 是 pytest **自带的一个 fixture** —— 和 `api_client` 一样，写进用例签名里就能用，不用 import、不用装东西。
import pytest,logging
from sqlalchemy.exc import OperationalError
from service.retry import retry_call


#证明：**它真的会重试**（第一次失败、第二次成功，最终拿到结果）




def test_retry_succeeds_on_second_attempt(caplog):
    caplog.set_level(logging.WARNING)
    calls = {"n": 0}# ← 本条用例私有

    def flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            raise OperationalError("SELECT 1", {}, Exception(2003, "Can't connect"))
        return "OK"

    result = retry_call(flaky, max_retries=2, delay=0)

    retry_logs = []
    for m in caplog.messages:
        if "次重试" in m:
            retry_logs.append(m)
    assert result == "OK"
    assert calls["n"] == 2
    assert len(retry_logs) == 1        # 只重试了一次
    assert "最终失败" not in caplog.text




#证明：**它不会无限重试**（一直失败时，试 3 次就放弃并抛出异常）




def test_retry_gives_up_after_max_attempts(caplog):
    caplog.set_level(logging.WARNING)
    calls = {"n": 0}

    def always():
        calls["n"] += 1       # 记一笔 “我又被调用了”，每被调用一次，+1
        raise OperationalError(
            "SELECT 1", {},
            Exception(2003, "Can't connect to MySQL server")
        )
    with pytest.raises(OperationalError):#执行下面那句，我预期它抛出 `OperationalError`。”
        retry_call(always, max_retries=2, delay=0)

    retry_logs = []
    for m in caplog.messages:
        if "次重试" in m:
            retry_logs.append(m)
    assert calls["n"] == 3
    assert len(retry_logs) == 2        # 重试了两次
    assert any("最终失败" in m for m in caplog.messages)



