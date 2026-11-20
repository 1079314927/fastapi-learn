import uuid
from service.database import SessionLocal
from service.models import AskLog




#同一个id发里两次相同问题
def test_same_request_id_writes_once(api_client):
    rid = f"test-idem-same-{uuid.uuid4().hex}"
    r1=api_client.post("/ask",json={"question": "直角三角形"},
                 headers={"X-Request-ID":rid})
    r2=api_client.post("/ask",json={"question": "直角三角形"},
                     headers={"X-Request-ID":rid})
    db = SessionLocal()
    n = db.query(AskLog).filter(AskLog.request_id == rid).count()
    db.close()
    assert n == 1
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()==r2.json()



#不同id发两次相同问题
def test_different_request_ids_write_two_rows(api_client):
    rid1 = f"test-idem-diff-{uuid.uuid4().hex}"
    rid2 = f"test-idem-diff-{uuid.uuid4().hex}"
    r1=api_client.post("/ask",json={"question": "直角三角形"},
                 headers={"X-Request-ID":rid1})
    r2=api_client.post("/ask",json={"question": "直角三角形"},
                     headers={"X-Request-ID":rid2})
    db = SessionLocal()
    n1 = db.query(AskLog).filter(AskLog.request_id == rid1).count()
    n2 = db.query(AskLog).filter(AskLog.request_id == rid2).count()
    db.close()
    assert n1 == 1 and n2 == 1
    assert r1.status_code == 200
    assert r2.status_code == 200

#不同id传相同不存在的问题，同时检测服务端能自己生成id且不同
def test_no_header_generates_distinct_id(api_client):
    q = f"test-noheader-{uuid.uuid4().hex}"
    r1=api_client.post("/ask",json={"question":q})
    r2=api_client.post("/ask",json={"question":q})
    #用不同名字否则被覆盖
    db = SessionLocal()
    rows = db.query(AskLog).filter(AskLog.question == q).order_by(AskLog.id).all()
    assert len(rows) == 2                    # 先确认条数，不然后面取值会越界
    assert rows[0].request_id                # ③ 第一条非空
    assert rows[1].request_id                # ③ 第二条非空
    assert rows[0].request_id != rows[1].request_id   # ④ 两者不相等
    #`request_id` 是服务端造的，**不带 `test-` 前缀**，`clean_ask_logs` 删不掉。跑十次就有二十条垃圾留在库里。断言做完要自己删
    db.query(AskLog).filter(AskLog.question == q).delete()
    db.commit()
    db.close()
    db.close()
    assert r1.status_code == 200
    assert r2.status_code == 200
