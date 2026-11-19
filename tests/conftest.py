import pytest,subprocess,sys,time,requests


from service.database import SessionLocal
from service.models import AskLog

SERVICE_DIR = r"D:\Code\fastapi-learn\service"
BASE = "http://127.0.0.1:8000"


class ApiClient:
    def __init__(self,base_url):
        self.base_url=base_url
        self.session=requests.Session()

    def get(self,path,**kwargs):
        kwargs.setdefault("timeout",10)
        return self.session.get(f"{self.base_url}{path}",**kwargs)

    def post(self,path,**kwargs):
        kwargs.setdefault("timeout",10)
        return self.session.post(f"{self.base_url}{path}",**kwargs)

    def close(self):
        self.session.close()


#启动服务器
@pytest.fixture(scope="session")
def server():
    proc=subprocess.Popen([sys.executable,"-m","uvicorn","main:app","--port","8000"],
                          cwd=SERVICE_DIR,
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL,)

    for _ in range(100):
        try:
            requests.get(f"{BASE}/health", timeout=1)
            break
        except requests.ConnectionError:
            time.sleep(0.2)
    else:
        proc.terminate()
        raise RuntimeError("服务器20秒内没起来")
    yield
    proc.terminate()
    proc.wait(timeout=10)

#获得网站地址
@pytest.fixture(scope="session")
def base_url(server):
    return BASE

#创建ApiClient的实例，调用方法创建连接，查看结果
@pytest.fixture(scope="session")
def api_client(base_url):
    c=ApiClient(base_url)
    yield c
    c.close()

#用会话清理用例产生的问题记录
@pytest.fixture(autouse=True)#每条用例自动用上，不用在参数里点名
def clean_ask_logs():
    db=SessionLocal()
    db.query(AskLog).filter(AskLog.request_id.like("test-%")).delete(synchronize_session=False)
    db.commit()
    db.close()
    yield